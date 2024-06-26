from enum import Enum

class ArchiveType(Enum):
	BIG = 1
	WAD = 2

class Format(Enum):
	UNKNOWN = 0
	SGES = 1
	FSB4 = 2
	BIN = 3
	TRM = 4
	OGG = 5
	BINK = 6
	FNT = 7
	DDS = 8
	ATB = 9
	FEV1 = 10
	CBF1 = 11
	PTM = 12
	TRLA = 13
	MP3 = 14
	RNM = 15

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
			case Format.MP3:
				from files.mp3 import MP3
				return MP3
			case _:
				from files.base import BaseFile
				return BaseFile
			
	@staticmethod
	def formatToExtension(format: Enum) -> str:
		match format:
			case Format.SGES:
				return "sges"
			case Format.FSB4:
				return "mp3"
			case Format.BIN:
				return "bin"
			case Format.TRM:
				return "trunk.pack"
			case Format.OGG:
				return "ogv"
			case Format.BINK:
				return "bik"
			case Format.FNT:
				return "fnt"
			case Format.DDS:
				return "dds"
			case Format.ATB:
				return "atb"
			case Format.FEV1:
				return "fev"
			case Format.CBF1:
				return "cotents"
			case Format.PTM:
				return "pack"
			case Format.TRLA:
				return "ids"
			case Format.MP3:
				return "mp3"
			case Format.RNM:
				return "roadnavdata"
			case _:
				return "unknown"
