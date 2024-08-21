from enum import Enum

class ArchiveType(Enum):
	BIG = 1
	WAD = 2

class Format(Enum):
	UNKNOWN = 0
	BIG = 1
	WAD = 2
	SGES = 3
	FSB4 = 4
	BIN = 5
	TRM = 6
	OGG = 7
	BINK = 8
	FNT = 9
	DDS = 10
	ATB = 11
	FEV1 = 12
	CBF1 = 13
	PTM = 14
	TRLA = 15
	MP3 = 16
	RNM = 17
	WAV = 18
	VRAM = 19

	@staticmethod
	def headerToFormat(header: str) -> Enum:
		match header:
			case "sges":
				return Format.SGES
			case "FSB4":
				return Format.FSB4
			case "DGAD":
				return Format.BIN
			case "trM#":
				return Format.TRM
			case "OggS":
				return Format.OGG
			case "BIKi":
				return Format.BINK
			case "FNT\x03":
				return Format.FNT
			case "DDS ":
				return Format.DDS
			case "ATB\x04":
				return Format.ATB
			case "FEV1":
				return Format.FEV1
			case "CBF1":
				return Format.CBF1
			case "ptM#":
				return Format.PTM
			case "TRLA":
				return Format.TRLA
			case "fffb9404":
				return Format.MP3
			case "RNM#":
				return Format.RNM
			case "VRAM":
				return Format.VRAM
			case _:
				return Format.UNKNOWN

	@staticmethod
	def formatToClass(format: Enum):
		match format:
			case Format.SGES:
				from files.sges import SGES
				return SGES
			case Format.FSB4:
				from files.fsb4 import FSB4
				return FSB4
			case Format.TRM:
				from files.trm import TRM
				return TRM
			case Format.OGG:
				from files.ogg import OGG
				return OGG
			case Format.BINK:
				from files.bink import BINK
				return BINK
			case Format.DDS:
				from files.dds import DDS
				return DDS
			case Format.ATB:
				from files.atb import ATB
				return ATB
			case Format.CBF1:
				from files.cbf import CBF
				return CBF
			case Format.PTM:
				from files.ptm import PTM
				return PTM
			case Format.MP3:
				from files.mp3 import MP3
				return MP3
			case Format.WAV:
				from files.base import BaseAudioFile
				return BaseAudioFile
			case Format.VRAM:
				from files.trm.vram import VRAM
				return VRAM
			case _:
				from files.base import BaseFile
				return BaseFile
			
	@staticmethod
	def formatToExtension(format: Enum) -> str:
		match format:
			case Format.SGES:
				return ".sges"
			case Format.FSB4:
				return ".mp3"
			case Format.BIN:
				return ".bin"
			case Format.TRM:
				return ".trunk.pack"
			case Format.OGG:
				return ".ogv"
			case Format.BINK:
				return ".bik"
			case Format.FNT:
				return ".fnt"
			case Format.DDS:
				return ".dds"
			case Format.ATB:
				return ".atb"
			case Format.FEV1:
				return ".fev"
			case Format.CBF1:
				return ".contents"
			case Format.PTM:
				return ".pack"
			case Format.TRLA:
				return ".ids"
			case Format.MP3:
				return ".mp3"
			case Format.RNM:
				return ".roadnavdata"
			case Format.WAV:
				return ".wav"
			case Format.VRAM:
				return ".vram"
			case _:
				return ".unknown"

def format_file_size(num: float):
    for unit in ("", "K", "M", "G", "T", "P", "E", "Z"):
        if abs(num) < 1000.0:
            return f"{num:3.1f} {unit}B"
        num /= 1000.0
    return f"{num:.1f}YB"
