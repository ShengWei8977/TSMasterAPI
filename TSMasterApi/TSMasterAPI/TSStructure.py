'''
Author: seven 865762826@qq.com
Date: 2023-04-21 10:21:17
LastEditors: seven 865762826@qq.com
LastEditTime: 2023-07-06 20:32:20
'''
from ctypes import Structure,c_char,c_int32,c_bool,c_uint8,c_int64,c_uint64,c_uint32,c_uint16,c_double,c_char_p,byref,string_at,string_at,CDLL,CFUNCTYPE,POINTER,pointer,c_void_p,c_float,c_int16,c_int8,WINFUNCTYPE


u8 = c_uint8
pu8 = POINTER(c_uint8)
s8 = c_int8
ps8 = POINTER(c_int8)

u16 = c_uint16
pu16 = POINTER(c_uint16)
s16 = c_int16
ps16 = POINTER(c_int16)

u32 = c_uint32
pu32 = POINTER(c_uint32)
s32 = c_int32
ps32 = POINTER(c_int32)
s64 = c_int64
ps64 = POINTER(c_int64)
u64 = c_uint64
pu64 = POINTER(c_uint64)
double = c_double
pdouble = POINTER(c_double)
charpp = POINTER(c_char_p)








DLC_DATA_BYTE_CNT = (
    0, 1, 2, 3, 4, 5, 6, 7,
    8, 12, 16, 20, 24, 32, 48, 64
)

TS_ReturnType = c_int32

class TLIBTSMapping(Structure):
    '''
    通道映射结构体
    字段赋值,使用TSMaster进行连接后,点击通道选择界面的"C"图标进行查看
    使用函数:tsapp_set_mapping
    '''
    _pack_ = 1
    _fields_ = [("FAppName", c_char * 32),
                ("FAppChannelIndex", c_int32),
                ("FAppChannelType", c_int32),
                ("FHWDeviceType", c_int32),
                ("FHWIndex", c_int32),
                ("FHWChannelIndex", c_int32),
                ("FHWDeviceSubType", c_int32),
                ("FHWDeviceName", c_char * 32),
                ("FMappingDisabled", c_bool),
                ]
PLIBTSMapping = POINTER(TLIBTSMapping)
class TLIBCAN(Structure):
    '''
    CAN报文结构体
    关联函数：
    tsapp_transmit_can_async 发送报文
    tsfifo_receive_can_msgs  接收报文
    '''
    _pack_ = 1
    _fields_ = [("FIdxChn", c_uint8),   #通道
                ("FProperties", c_uint8),#属性定义：[7] 0-normal frame, 1-error frame
                                                # [6] 0-not logged, 1-already logged
                                                # [5-3] tbd
                                                # [2] 0-std frame, 1-extended frame
                                                # [1] 0-data frame, 1-remote frame
                                                # [0] dir: 0-RX, 1-TX 

                ("FDLC", c_uint8),           # dlc from 0 to 8
                ("FReserved", c_uint8),
                ("FIdentifier", c_int32),   #ID
                ("FTimeUs", c_int64),      #时间戳
                ("FData", c_uint8 * 8),    #报文数据
                ]
    def __init__(self, FIdxChn=0, FDLC=8, FIdentifier=0x1, FProperties=1, FData=[]):
        self.FIdxChn = FIdxChn
        self.FDLC = FDLC
        if self.FDLC > 8:
            self.FDLC = 8
        self.FIdentifier = FIdentifier
        self.FProperties = FProperties
        for i in range(len(FData)):
            self.FData[i] = FData[i]

    def set_data(self, data):
        lengh = len(data)
        if lengh > self.FDLC:
            lengh = self.FDLC
        for i in range(lengh):
            self.FData[i] = data[i]

    def __str__(self):
        field_strings = [f"Timestamp: {self.FTimeUs:>15.6f}"]

        field_strings.append(f"Channel: {self.FIdxChn}")

        if (self.FProperties >> 2 & 1) == 1:
            FIdentifier = f"ID: {self.FIdentifier:08x}"
        else:
            FIdentifier = f"ID: {self.FIdentifier:04x}"
        field_strings.append(FIdentifier.rjust(12, " "))
        flag_string = " ".join(
            [
                "ext" if (self.FProperties >> 2 & 1) == 1 else "std",
                "Rx" if (self.FProperties & 1) == 0 else "Tx",
                "E" if self.FProperties == 0x80 else " ",
                "R" if (self.FProperties >> 1 & 1) == 1 else " ",
            ]
        )
        field_strings.append(flag_string)
        field_strings.append(f"DL: {self.FDLC:2d}")
        data_strings = []
        for i in range(self.FDLC):
            data_strings.append(f"{self.FData[i]:02x}")
        field_strings.append(" ".join(data_strings).ljust(24, " "))
        return "    ".join(field_strings).strip()
    
PCAN = POINTER(TLIBCAN)

class TLIBCANFD(Structure):
    '''
    CANFD报文结构体
    关联函数：
    tsapp_transmit_canfd_async 发送报文
    tsfifo_receive_canfd_msgs  接收报文
    '''
    _pack_ = 1
    _fields_ = [("FIdxChn", c_uint8),       #通道
                ("FProperties", c_uint8),   #属性 # [7] 0-normal frame, 1-error frame
                                            # [6] 0-not logged, 1-already logged
                                            # [5-3] tbd
                                            # [2] 0-std frame, 1-extended frame
                                            # [1] 0-data frame, 1-remote frame
                                            # [0] dir: 0-RX, 1-TX
                ("FDLC", c_uint8),          # dlc from 0 to 15
                ("FFDProperties", c_uint8), #FD属性 
                                            # [2] ESI, The E RROR S TATE I NDICATOR (ESI) flag is transmitted dominant by error active nodes, recessive by error passive nodes. ESI does not exist in CAN format frames
                                            # [1] BRS, If the bit is transmitted recessive, the bit rate is switched from the standard bit rate of the A RBITRATION P HASE to the preconfigured alternate bit rate of the D ATA P HASE . If it is transmitted dominant, the bit rate is not switched. BRS does not exist in CAN format frames.
                                            # [0] EDL: 0-normal CAN frame, 1-FD frame, added 2020-02-12, The E XTENDED D 
                ("FIdentifier", c_int32),   #ID
                ("FTimeUs", c_uint64),   #时间戳
                ("FData", c_uint8 * 64),    #数据
                ]
    def __init__(self, FIdxChn=0, FDLC=8, FIdentifier=0x1, FProperties=1, FFDProperties=1, FData=[]):

        self.FIdxChn = FIdxChn
        self.FDLC = FDLC
        if self.FDLC > 15:
            self.FDLC = 15
        self.FIdentifier = FIdentifier
        self.FProperties = FProperties
        self.FFDProperties = FFDProperties
        for i in range(len(FData)):
            self.FData[i] = FData[i]

    def set_data(self, data):
        lengh = len(data)
        if lengh > DLC_DATA_BYTE_CNT(self.FDLC):
            lengh = DLC_DATA_BYTE_CNT(self.FDLC)
        for i in range(lengh):
            self.FData[i] = data[i]

    def __str__(self):
        field_strings = [f"Timestamp: {self.FTimeUs:>15.6f}"]

        field_strings.append(f"Channel: {self.FIdxChn}")

        if (self.FProperties >> 2 & 1) == 1:
            FIdentifier = f"ID: {self.FIdentifier:08x}"
        else:
            FIdentifier = f"ID: {self.FIdentifier:04x}"
        field_strings.append(FIdentifier.rjust(12, " "))
        flag_string = " ".join(
            [
                "ext" if (self.FProperties >> 2 & 1) == 1 else "std",
                "Rx" if (self.FProperties & 1) == 0 else "Tx",
                "E" if self.FProperties == 0x80 else " ",
                "R" if (self.FProperties >> 1 & 1) == 1 else " ",
                "F" if (self.FFDProperties & 1 == 1) else " ",
                "BS" if (self.FFDProperties >> 1 & 1 == 1) else "  ",
                "EI" if (self.FFDProperties >> 2 & 1 == 1) else "  ",
            ]
        )
        field_strings.append(flag_string)
        field_strings.append(f"DL: {self.FDLC:2d}")
        data_strings = []
        for i in range(DLC_DATA_BYTE_CNT[self.FDLC]):
            data_strings.append(f"{self.FData[i]:02x}")
        field_strings.append(" ".join(data_strings).ljust(24, " "))
        return "    ".join(field_strings).strip()

PCANFD = POINTER(TLIBCANFD)

class TLIBLIN(Structure):
    '''
    LIN报文结构体
    关联函数：
    tsapp_transmit_lin_async 发送报文
    tsfifo_receive_lin_msgs  接收报文
    '''
    _pack_ = 1
    _fields_ = [("FIdxChn", c_uint8),       # channel index starting from 0
                ("FErrStatus", c_uint8),    #  0: normal
                ("FProperties", c_uint8),   # [7] tbd
                                            # [6] 0-not logged, 1-already logged
                                            # [5-4] FHWType #DEV_MASTER,DEV_SLAVE,DEV_LISTENER
                                            # [3] 0-not ReceivedSync, 1- ReceivedSync
                                            # [2] 0-not received FReceiveBreak, 1-Received Break
                                            # [1] 0-not send FReceiveBreak, 1-send Break
                                            # [0] dir: 0-RX, 1-TX
                ("FDLC", c_uint8),          # dlc from 0 to 8
                ("FIdentifier", c_uint8),    #ID
                ("FChecksum", c_uint8),     # LIN checksum
                ("FStatus", c_uint8),       # place holder 1
                ("FTimeUs", c_int64),       # 时间戳
                ("FData", c_uint8 * 8),     # 报文数据
                ]
    def __init__(self,FIdxChn = 0,FDLC = 8,FIdentifier = 0x1,FProperties = 1,FData=[]):
        self.FIdxChn = FIdxChn
        self.FDLC = FDLC
        if self.FDLC > 8:
            self.FDLC = 8
        self.FIdentifier = FIdentifier
        self.FProperties = FProperties
        for i in range(len(FData)):
            self.FData[i] = FData[i]
    def set_data(self, data):
        lengh = len(data)
        if lengh > DLC_DATA_BYTE_CNT(self.FDLC):
            lengh = DLC_DATA_BYTE_CNT(self.FDLC)
        for i in range(lengh):
            self.FData[i] = data[i]
    def __str__(self):
        field_strings = [f"Timestamp: {self.FTimeUs:>15.6f}"]

        field_strings.append(f"Channel: {self.FIdxChn}")

        FIdentifier = f"ID: {self.FIdentifier:04x}"

        field_strings.append(FIdentifier.rjust(12, " "))
        
        field_strings.append(f"DL: {self.FDLC:2d}")
        data_strings = []
        for i in range(self.FDLC):
            data_strings.append(f"{self.FData[i]:02x}")
        field_strings.append(" ".join(data_strings).ljust(24, " "))
        return "    ".join(field_strings).strip()
    
PLIN = POINTER(TLIBLIN)

class TLIBFlexray(Structure):
    _pack_ = 1
    _fields_ = [("FIdxChn", c_uint8),
                ("FChannelMask", c_uint8),
                ("FDir", c_uint8),
                ("FPayloadLength", c_uint8),
                ("FActualPayloadLength", c_uint8),
                ("FCycleNumber", c_uint8),
                ("FCCType", c_uint8),
                ("FReserved0", c_uint8),
                ("FHeaderCRCA", c_uint16),
                ("FHeaderCRCB", c_uint16),
                ("FFrameStateInfo", c_uint16),
                ("FSlotId", c_uint16),
                ("FFrameFlags", c_uint32),
                ("FFrameCRC", c_uint32),
                ("FReserved1", c_uint64),
                ("FReserved2", c_uint64),
                ("FTimeUs", c_uint64),
                ("FData", c_uint8 * 254),
                ]
    def __init__(self,FIdxChn=0,FSlotId=1,FChannelMask=1,FActualPayloadLength=32,FCycleNumber=1,FData=[]):
        self.FIdxChn = FIdxChn
        self.FSlotId = FSlotId
        self.FChannelMask = FChannelMask | 0x04
        self.FActualPayloadLength = FActualPayloadLength
        self.FCycleNumber = FCycleNumber  
        self.FPayloadLength = 254  
        datalen = len(FData)
        if datalen>self.FActualPayloadLength:
            datalen = self.FActualPayloadLength
        for i in range(datalen):
            self.FData[i] = FData[i]
    def set_data(self,data):
        datalen = len(data)
        if datalen>self.FActualPayloadLength:
            datalen = self.FActualPayloadLength
        for i in range(datalen):
            self.FData[i] = data[i]
    def __str__(self):
        field_strings = [f"Timestamp: {self.FTimeUs:>15.6f}"]
        FRChannel = str(self.FIdxChn+1) + 'A'
        if (self.FChannelMask & 3) == 1:
            FRChannel = str(self.FIdxChn+1) + 'A'
        elif (self.FChannelMask & 3) == 2:
            FRChannel = str(self.FIdxChn+1) + 'B'
        elif (self.FChannelMask & 3) == 3:
            FRChannel = str(self.FIdxChn+1) + 'AB'
        
        field_strings.append(f"FRChannel: {FRChannel}")

        FIdentifier = f"SlotID: {self.FSlotId}"

        field_strings.append(FIdentifier.rjust(12, " "))
        field_strings.append(str(self.FCycleNumber).rjust(2, " "))
        field_strings.append(f"DL: {self.FActualPayloadLength}")
        data_strings = []
        for i in range(self.FActualPayloadLength):
            data_strings.append(f"{self.FData[i]:02x}")
        field_strings.append(" ".join(data_strings).ljust(24, " "))
        return "    ".join(field_strings).strip()
    
PFlexray = POINTER(TLIBFlexray)    

class TLibFlexray_controller_config(Structure):
    """
    Flexray controller config结构体
    作用:在配置flexray时,需要对硬件参数进行配置
    字段来源:数据库中可获取
    注:在使用该库时,可直接TSMaster加载工程,跳过复杂参数的配置
    关联函数:tsflexray_set_controller_frametrigger
    """
    _pack_ = 1
    _fields_ = [("NETWORK_MANAGEMENT_VECTOR_LENGTH", c_uint8),
                ("PAYLOAD_LENGTH_STATIC", c_uint8),
                ("FReserved", c_uint16),
                ("LATEST_TX", c_uint16),
                ("T_S_S_TRANSMITTER", c_uint16),
                ("CAS_RX_LOW_MAX", c_uint8),
                ("SPEED", c_uint8),
                ("WAKE_UP_SYMBOL_RX_WINDOW", c_uint16),
                ("WAKE_UP_PATTERN", c_uint8),
                ("WAKE_UP_SYMBOL_RX_IDLE", c_uint8),
                ("WAKE_UP_SYMBOL_RX_LOW", c_uint8),
                ("WAKE_UP_SYMBOL_TX_IDLE", c_uint8),
                ("WAKE_UP_SYMBOL_TX_LOW", c_uint8),
                ("channelAConnectedNode", c_uint8),
                ("channelBConnectedNode", c_uint8),
                ("channelASymbolTransmitted", c_uint8),
                ("channelBSymbolTransmitted", c_uint8),
                ("ALLOW_HALT_DUE_TO_CLOCK", c_uint8),
                ("SINGLE_SLOT_ENABLED", c_uint8),
                ("wake_up_idx", c_uint8),
                ("ALLOW_PASSIVE_TO_ACTIVE", c_uint8),
                ("COLD_START_ATTEMPTS", c_uint8),
                ("synchFrameTransmitted", c_uint8),
                ("startupFrameTransmitted", c_uint8),
                ("LISTEN_TIMEOUT", c_uint32),
                ("LISTEN_NOISE", c_uint8),
                ("MAX_WITHOUT_CLOCK_CORRECTION_PASSIVE", c_uint8),
                ("MAX_WITHOUT_CLOCK_CORRECTION_FATAL", c_uint8),
                ("REVERS0", c_uint8),
                ("MICRO_PER_CYCLE", c_uint32),
                ("Macro_Per_Cycle", c_uint16),
                ("SYNC_NODE_MAX", c_uint8),
                ("REVERS1", c_uint8),
                ("MICRO_INITIAL_OFFSET_A", c_uint8),
                ("MICRO_INITIAL_OFFSET_B", c_uint8),
                ("MACRO_INITIAL_OFFSET_A", c_uint8),
                ("MACRO_INITIAL_OFFSET_B", c_uint8),
                ("N_I_T", c_uint16),
                ("OFFSET_CORRECTION_START", c_uint16),
                ("DELAY_COMPENSATION_A", c_uint8),
                ("DELAY_COMPENSATION_B", c_uint8),
                ("CLUSTER_DRIFT_DAMPING", c_uint8),
                ("DECODING_CORRECTION", c_uint8),
                ("ACCEPTED_STARTUP_RANGE", c_uint16),
                ("MAX_DRIFT", c_uint16),
                ("STATIC_SLOT", c_uint16),
                ("NUMBER_OF_STATIC_SLOTS", c_uint16),
                ("MINISLOT", c_uint8),
                ("REVERS2", c_uint8),
                ("NUMBER_OF_MINISLOTS", c_uint16),
                ("DYNAMIC_SLOT_IDLE_PHASE", c_uint8),
                ("ACTION_POINT_OFFSET", c_uint8),
                ("MINISLOT_ACTION_POINT_OFFSET", c_uint8),
                ("REVERS3", c_uint8),
                ("OFFSET_CORRECTION_OUT", c_uint16),
                ("RATE_CORRECTION_OUT", c_uint16),
                ("EXTERN_OFFSET_CORRECTION", c_uint8),
                ("EXTERN_RATE_CORRECTION", c_uint8),
                ("config1_byte", c_uint8),
                ("config_byte", c_uint8),  # bit0: 1：启用cha上终端电阻 0：不启用
                # bit1: 1：启用chb上终端电阻 0：不启用
                # bit2: 1：启用接收FIFO     0：不启用
                # bit4: 1：cha桥接使能    0：不使能
                # bit5: 1：chb桥接使能    0：不使能
                # bit6: 1:not ignore NULL Frame  0: ignore NULL Frame
                ]
    def set_controller_config(self,xml_,is_open_a=True, is_open_b=True, wakeup_chn=0, enable100_a=True, enable100_b=True,is_show_nullframe=True, is_Bridging=False):
        if isinstance(xml_,dict):
            self.NETWORK_MANAGEMENT_VECTOR_LENGTH = xml_['NETWORK_MANAGEMENT_VECTOR_LENGTH']
            self.PAYLOAD_LENGTH_STATIC = xml_['PAYLOAD_LENGTH_STATIC']
            self.LATEST_TX = xml_['LATEST_TX']
            self.T_S_S_TRANSMITTER = xml_['T_S_S_TRANSMITTER']
            self.CAS_RX_LOW_MAX = xml_['CAS_RX_LOW_MAX']
            self.SPEED = xml_['SPEED']
            self.WAKE_UP_SYMBOL_RX_WINDOW = xml_['WAKE_UP_SYMBOL_RX_WINDOW']
            self.WAKE_UP_PATTERN = xml_['WAKE_UP_PATTERN']
            self.WAKE_UP_SYMBOL_RX_IDLE = xml_['WAKE_UP_SYMBOL_RX_IDLE']
            self.WAKE_UP_SYMBOL_RX_LOW = xml_['WAKE_UP_SYMBOL_RX_LOW']
            self.WAKE_UP_SYMBOL_TX_IDLE = xml_['WAKE_UP_SYMBOL_TX_IDLE']
            self.WAKE_UP_SYMBOL_TX_LOW = xml_['WAKE_UP_SYMBOL_TX_LOW']
            self.channelAConnectedNode = 1 if is_open_a else 0
            self.channelBConnectedNode = 1 if is_open_b else 0
            self.channelASymbolTransmitted = 1  
            self.channelBSymbolTransmitted = 1  
            self.ALLOW_HALT_DUE_TO_CLOCK = xml_['ALLOW_HALT_DUE_TO_CLOCK']
            self.SINGLE_SLOT_ENABLED = xml_['SINGLE_SLOT_ENABLED']
            self.wake_up_idx = wakeup_chn
            self.ALLOW_PASSIVE_TO_ACTIVE = xml_['ALLOW_PASSIVE_TO_ACTIVE']
            self.COLD_START_ATTEMPTS = xml_['COLD_START_ATTEMPTS']
            self.synchFrameTransmitted = 1
            self.startupFrameTransmitted = xml_['startupFrameTransmitted']
            self.LISTEN_TIMEOUT = xml_['LISTEN_TIMEOUT']
            self.LISTEN_NOISE = xml_['LISTEN_NOISE']
            self.MAX_WITHOUT_CLOCK_CORRECTION_PASSIVE = xml_['MAX_WITHOUT_CLOCK_CORRECTION_PASSIVE']
            self.MAX_WITHOUT_CLOCK_CORRECTION_FATAL = xml_['MAX_WITHOUT_CLOCK_CORRECTION_FATAL']
            self.MICRO_PER_CYCLE = xml_['MICRO_PER_CYCLE']
            self.Macro_Per_Cycle = xml_['MACRO_PER_CYCLE']
            self.SYNC_NODE_MAX = xml_['SYNC_NODE_MAX']
            self.MICRO_INITIAL_OFFSET_A = xml_['MICRO_INITIAL_OFFSET_A']
            self.MICRO_INITIAL_OFFSET_B = xml_['MICRO_INITIAL_OFFSET_B']
            self.MACRO_INITIAL_OFFSET_A = xml_['MACRO_INITIAL_OFFSET_A']
            self.MACRO_INITIAL_OFFSET_B = xml_['MACRO_INITIAL_OFFSET_B']
            self.N_I_T = xml_['N_I_T']
            self.OFFSET_CORRECTION_START = xml_['OFFSET_CORRECTION_START']
            self.DELAY_COMPENSATION_A = xml_['DELAY_COMPENSATION_A']
            self.DELAY_COMPENSATION_B = xml_['DELAY_COMPENSATION_B']
            self.CLUSTER_DRIFT_DAMPING = xml_['CLUSTER_DRIFT_DAMPING']
            self.DECODING_CORRECTION = xml_['DECODING_CORRECTION']
            self.ACCEPTED_STARTUP_RANGE = xml_['ACCEPTED_STARTUP_RANGE']
            self.MAX_DRIFT = xml_['MAX_DRIFT']
            self.STATIC_SLOT = xml_['STATIC_SLOT']
            self.NUMBER_OF_STATIC_SLOTS = xml_['NUMBER_OF_STATIC_SLOTS']
            self.MINISLOT = xml_['MINISLOT']
            self.NUMBER_OF_MINISLOTS = xml_['NUMBER_OF_MINISLOTS']
            self.DYNAMIC_SLOT_IDLE_PHASE = xml_['DYNAMIC_SLOT_IDLE_PHASE']
            self.ACTION_POINT_OFFSET = xml_['ACTION_POINT_OFFSET']
            self.MINISLOT_ACTION_POINT_OFFSET = xml_['MINISLOT_ACTION_POINT_OFFSET']
            self.OFFSET_CORRECTION_OUT = xml_['OFFSET_CORRECTION_OUT']
            self.RATE_CORRECTION_OUT = xml_['RATE_CORRECTION_OUT']
            self.EXTERN_OFFSET_CORRECTION = xml_['EXTERN_OFFSET_CORRECTION']
            self.EXTERN_RATE_CORRECTION = xml_['EXTERN_RATE_CORRECTION']
            self.config1_byte = 1
                # if
            self.config_byte = 0xc
            if is_Bridging:
                    self.config_byte = 0x3c
            self.config_byte = self.config_byte | (0x1 if enable100_a else 0x00) | (0x2 if enable100_b else 0x00) | (0x40 if is_show_nullframe else 0x00)
        return self
PLibFlexray_controller_config = POINTER(TLibFlexray_controller_config) 
class TLibTrigger_def(Structure):
    """
    Trigger 结构体
    作用:调度表,配置要下发的报文
    关联函数:tsflexray_set_controller_frametrigger
    """
    _pack_ = 1
    _fields_ = [("slot_id", c_uint16),   #slot ID
                ("frame_idx", c_uint8),  #Frame id
                ("cycle_code", c_uint8), #base_cycle+rep_cycle
                ("config_byte", c_uint8),  # bit0: 是否使能通道A
                # bit1: 是否使能通道B
                # bit2: 是否网络管理报文
                # bit3: 传输模式，0 表示连续传输，1表示单次触发
                # bit4: 是否为冷启动报文，只有缓冲区0可以置1
                # bit5: 是否为同步报文，只有缓冲区0 / 1 可以置1
                # bit6:
                # bit7: 帧类型：0 - 静态，1 - 动态
                ("recv", c_uint8),
                ]
PLibTrigger_def = POINTER(TLibTrigger_def)
class TLIBHWInfo(Structure):
    """
    描述:TLib 的硬件信息结构体类型
    """
    _pack_ = 1
    _fields_ = [("FDeviceType", c_int32),
                ("FDeviceIndex", c_int32),
                ("FVendorName", c_char * 32),
                ("FDeviceName", c_char * 32),
                ("FSerialString", c_char * 64),
                ]

PLIBHWInfo = POINTER(TLIBHWInfo)

DATABASE_STR_LEN = 512    

class TCANSignal(Structure):
    '''
    CAN Signal 
    '''
    _pack_ = 1
    _fields_ = [("FCANSgnType", c_uint8),
                ("FIsIntel", c_bool),
                ("FStartBit", c_int32),
                ("FLength", c_int32),
                ("FFactor", c_double),
                ("FOffset", c_double),
                ]
PCANSignal = POINTER(TCANSignal)    
class TLINSignal(Structure):
    '''
    LIN Signal 
    '''
    _pack_ = 1
    _fields_ = [("FLINSgnType", c_uint8),
                ("FIsIntel", c_bool),
                ("FStartBit", c_int32),
                ("FLength", c_int32),
                ("FFactor", c_double),
                ("FOffset", c_double),
                ]
PLINSignal = POINTER(TLINSignal)      
class TFlexRaySignal(Structure):
    '''
    获取信号在数据库中的定义 通过该结构体 可获取对报文中该信号值以及设置对应报文该信号值
    相关函数：
    tscom_flexray_get_signal_definition
    tscom_flexray_set_signal_value_in_raw_frame
    tscom_flexray_get_signal_value_in_raw_frame
    函数使用示例可在Flexray_demo中找到
    '''
    _pack_ =1
    _fields_ = [
                ("FFRSgnType",c_uint8),
                ("FCompuMethod",c_uint8),
                ("FReserved",c_uint8),
                ("FIsIntel",c_bool),
                ("FStartBit",c_int32),
                ("FUpdateBit",c_int32),
                ("FLength",c_int32),
                ("FFactor",c_double),
                ("FOffset",c_double),
                ] 
PFlexRaySignal = POINTER(TFlexRaySignal)
class TDBProperties(Structure):
    '''
    DataBase properties 描述数据库中的报文数量 信号数量 ECU节点数量
    '''
    _pack_ = 1
    _fields_ = [("FDBIndex", c_int32),
                ("FSignalCount", c_int32),
                ("FFrameCount", c_int32),
                ("FECUCount", c_int32),
                ("FSupportedChannelMask", c_uint64),
                ("FName", c_char * DATABASE_STR_LEN),
                ("FComment", c_char * DATABASE_STR_LEN),
                ("FFlags", u64),
                ]
PDBProperties = POINTER(TDBProperties)
class TDBECUProperties(Structure):
    '''
    DataBase ECU properties 描述数据库中ECU节点 TX RX报文数量以及ECU节点名称与注释
    '''
    _pack_ = 1
    _fields_ = [("FDBIndex", c_int32),
                ("FECUIndex", c_int32),
                ("FTxFrameCount", c_int32),
                ("FRxFrameCount", c_int32),
                ("FName", c_char * DATABASE_STR_LEN),
                ("FComment", c_char * DATABASE_STR_LEN),
                ]
PDBECUProperties = POINTER(TDBECUProperties) 
class TDBFrameProperties(Structure):
    '''
    DataBase Frame properties 描述数据库中Frame signal数量以及Frame名称与注释
    '''
    _pack_ = 1
    _fields_ = [("FDBIndex", c_int32),
                ("FECUIndex", c_int32),
                ("FFrameIndex", c_int32),
                ("FIsTx", c_uint8),
                ("FReserved1", c_uint8),
                ("FReserved2", c_uint8),
                ("FReserved3", c_uint8),
                ("FFrameType", c_int32),
                # CAN
                ("FCANIsDataFrame", c_uint8),
                ("FCANIsStdFrame", c_uint8),
                ("FCANIsEdl", c_uint8),
                ("FCANIsBrs", c_uint8),
                ("FCANIdentifier", c_int32),
                ("FCANDLC", c_int32),
                ("FCANDataBytes", c_int32),
                #LIN
                ("FLINIdentifier", c_int32),
                ("FLINDLC", c_int32),
                #FLEXRAY
                ("FFRChannelMask", c_uint8),
                ("FFRBaseCycle", c_uint8),
                ("FFRCycleRepetition", c_uint8),
                ("FFRIsStartupFrame", c_uint8),
                ("FFRSlotId", c_uint16),
                ("FFRDLC", c_uint16),
                ("FFRCycleMask", c_uint64),
                ("FSignalCount", c_int32),
                ("FName", c_char * DATABASE_STR_LEN),
                ("FComment", c_char * DATABASE_STR_LEN),
                ] 
PDBFrameProperties = POINTER(TDBFrameProperties)     
class TDBSignalProperties(Structure):
    '''
    DataBase Signal properties 描述数据库中 signal详细信息
    '''
    _pack_ = 1
    _fields_ = [("FDBIndex", c_int32),
                ("FECUIndex", c_int32),
                ("FFrameIndex", c_int32),
                ("FSignalIndex", c_int32),
                ("FIsTx", c_uint8),
                ("FReserved1", c_uint8),
                ("FReserved2", c_uint8),
                ("FReserved3", c_uint8),
                ("FSignalType", c_int32),
                ("FCANSignal", TCANSignal),
                ("FLINSignal", TLINSignal),
                ("FFlexRaySignal", TFlexRaySignal),
                ("FParentFrameId", c_int32),
                ("FInitValue", c_double),
                ("FName", c_char * DATABASE_STR_LEN),
                ("FComment", c_char * DATABASE_STR_LEN),
                ] 

PDBSignalProperties = POINTER(TDBSignalProperties) 

GENERIC_STRING_MAX_LENGTH = 32
class TFlexRayClusterParameters(Structure):
    '''
    DataBase Signal properties 描述数据库中 signal详细信息
    '''
    _pack_ = 1
    _fields_ = [("FShortName", c_char * GENERIC_STRING_MAX_LENGTH),
                ("FLongName", c_char * GENERIC_STRING_MAX_LENGTH),
                ("FDescription", c_char * GENERIC_STRING_MAX_LENGTH),
                ("FSpeed", c_char * GENERIC_STRING_MAX_LENGTH),
                ("FChannels", c_char * GENERIC_STRING_MAX_LENGTH),
                ("FBitCountingPolicy", c_char * GENERIC_STRING_MAX_LENGTH),
                ("FProtocol", c_char * GENERIC_STRING_MAX_LENGTH),
                ("FProtocolVersion", c_char * GENERIC_STRING_MAX_LENGTH),
                ("FMedium",  c_char * GENERIC_STRING_MAX_LENGTH),
                ("FIsHighLowBitOrder", s32),
                ("FMaxFrameLengthByte", s32),
                ("FNumberOfCycles", s32),
                ("FCycle_us", s32),
                ("FBit_us", double),
                ("FSampleClockPeriod_us", double),
                ("FMacrotick_us", double),

                ("FMacroPerCycle", s32),
                ("FNumberOfStaticSlots", s32),
                ("FStaticSlot_MT", s32),
                ("FActionPointOffset_MT", s32),
                ("FPayloadLengthStatic_WORD", s32),
                ("FNumberOfMiniSlots", s32),
                ("FMiniSlot_MT", s32),
                ("FMiniSlotActionPointOffset_MT", s32),
                ("FDynamicSlotIdlePhase_MiniSlots", s32),
                ("FSymbolWindow_MT", s32),
                ("FNIT_MT", s32),
                ("FSyncNodeMax", s32),
                ("FNetworkManagementVectorLength", s32),
                ("FListenNoise", s32),
                ("FColdStartAttempts", s32),
                ("FCASRxLowMax_gdBit", s32),
                ("FWakeupSymbolRxIdle_gdBit", s32),
                ("FWakeupSymbolRxLow_gdBit", s32),
                ("FWakeupSymbolRxWindow_gdBit", s32),
                ("FWakeupSymbolTxIdle_gdBit", s32),
                ("FWakeupSymbolTxLow_gdBit", s32),
                ("FMaxInitializationError_us", double),
                ("FClusterDriftDamping_uT", s32),
                ("FOffsetCorrectionStart_MT", s32),
                ("FMaxWithoutClockCorrectionFatal", s32),
                ("FMaxWithoutClockCorrectionPassive", s32),
                ] 
PFlexRayClusterParameters = POINTER(TFlexRayClusterParameters)


class TFlexRayControllerParameters(Structure):
    '''
    DataBase Signal properties 描述数据库中 signal详细信息
    '''
    _pack_ = 1
    _fields_ = [("FShortName", c_char * GENERIC_STRING_MAX_LENGTH),
                ("FConnectedChannels", c_char * GENERIC_STRING_MAX_LENGTH),
                ("FMicroPerCycle_uT", s32),
                ("FMicroPerMacroNom_uT", s32),
                ("FMicroTick_us", double),
                ("FSamplesPerMicrotick", s32),
                ("FWakeupChannelA", s32),
                ("FWakeupChannelB", s32),
                ("FMaxDrift_uT", s32),
                ("FWakeupPattern", s32),
                ("FListenTimeout_uT", s32),
                ("FAcceptedStartupRange_uT", s32),
                ("FMacroInitialOffsetA_MT", s32),
                ("FMacroInitialOffsetB_MT", s32),
                ("FMicroInitialOffsetA_uT", s32),
                ("FMicroInitialOffsetB_uT", s32),
                ("FKeySlotUsage", c_char * GENERIC_STRING_MAX_LENGTH),
                ("FKeySlotID", s32),
                ("FSingleSlotEnabled", s32),
                ("FClusterDriftDamping_uT", s32),
                ("FDocodingCorrection_uT", s32),
                ("FDelayCompensationA_uT", s32),
                ("FDelayCompensationB_uT", s32),
                ("FOffsetCorrectionOut_uT", s32),
                ("FExternRateCorrection_uT", s32),
                ("FRateCorrectionOut_uT", s32),
                ("FExternOffsetCorrection_uT", s32),
                ("FAllowHaltDueToClock", s32),
                ("FAllowPassivToActive", s32),
                ("FLatestTx", s32),
                ("FMaxDynamicPayloadLength", s32),
                ] 

PFlexRayControllerParameters = POINTER(TFlexRayControllerParameters) 

#回调函数

OnTx_RxFUNC_CANFD = WINFUNCTYPE(None, ps32, PCANFD)


OnTx_RxFUNC_CAN = WINFUNCTYPE(None, ps32, PCAN)


OnTx_RxFUNC_LIN = WINFUNCTYPE(None, ps32, PLIN)


OnTx_RxFUNC_Flexray = WINFUNCTYPE(None, ps32, PFlexray)