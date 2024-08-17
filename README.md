# Game Data

## Audio
Most of the case audio appears in `cases_1_1.big.pc`. The file are named with prefixes for each desk.

## Desks
This is speculation to the audio files prefixes and which desk.
- Patrol/Tutorial - `pt`
- Traffic - `at`, `ut`
- Homicide - `ah`, `uh`
- Vice - `av`
- Arson - `np`

- Robbery - `ur`
- Burglary - `ub`
- Bunco - `ub`

## Cases
- [Patrol](https://lanoire.fandom.com/wiki/Patrol) - `pt`
	- [Upon Reflection](https://lanoire.fandom.com/wiki/Upon_Reflection)
	- [Armed and Dangerous](https://lanoire.fandom.com/wiki/Armed_and_Dangerous)
	- [Warrants Outstanding](https://lanoire.fandom.com/wiki/Warrants_Outstanding)
	- [Buyer Beware](https://lanoire.fandom.com/wiki/Buyer_Beware)
- [Traffic](https://lanoire.fandom.com/wiki/Traffic) - `at`
	- [The Driver's Seat](https://lanoire.fandom.com/wiki/The_Driver's_Seat) - `at001`
	- [The Consul's Car](https://lanoire.fandom.com/wiki/The_Consul's_Car)
	- [A Marriage Made in Heaven](https://lanoire.fandom.com/wiki/A_Marriage_Made_in_Heaven) - `at003`
	- [A Slip of the Tongue](https://lanoire.fandom.com/wiki/A_Slip_of_the_Tongue)
	- [The Fallen Idol](https://lanoire.fandom.com/wiki/The_Fallen_Idol) - `at005`
- [Homicide](https://lanoire.fandom.com/wiki/Homicide) - `ah`
	- [The Red Lipstick Murder](https://lanoire.fandom.com/wiki/The_Red_Lipstick_Murder) - `ah001`
	- [The Golden Butterfly](https://lanoire.fandom.com/wiki/The_Golden_Butterfly) - `ah002`
	- [The Silk Stocking Murder](https://lanoire.fandom.com/wiki/The_Silk_Stocking_Murder)
	- [The White Shoe Slaying](https://lanoire.fandom.com/wiki/The_White_Shoe_Slaying) - `ah004`
	- [The Studio Secretary Murder](https://lanoire.fandom.com/wiki/The_Studio_Secretary_Murder) - `ah005`
	- [The Quarter Moon Murders](https://lanoire.fandom.com/wiki/The_Quarter_Moon_Murders) - `ah006`
- [Vice](https://lanoire.fandom.com/wiki/Vice) - `av`
	- [The Black Caesar](https://lanoire.fandom.com/wiki/The_Black_Caesar)
	- [Reefer Madness](https://lanoire.fandom.com/wiki/Reefer_Madness)
	- [The Set Up](https://lanoire.fandom.com/wiki/The_Set_Up)
	- [The Naked City](https://lanoire.fandom.com/wiki/The_Naked_City)
	- [Manifest Destiny](https://lanoire.fandom.com/wiki/Manifest_Destiny)
- [Arson](https://lanoire.fandom.com/wiki/Arson)
	- [The Gas Man](https://lanoire.fandom.com/wiki/The_Gas_Man)
	- [A Walk in Elysian Fields](https://lanoire.fandom.com/wiki/A_Walk_in_Elysian_Fields)
	- [House of Sticks](https://lanoire.fandom.com/wiki/House_of_Sticks)
	- [A Polite Invitation](https://lanoire.fandom.com/wiki/A_Polite_Invitation)
	- [Nicholson Electroplating](https://lanoire.fandom.com/wiki/Nicholson_Electroplating)
	- [A Different Kind of War](https://lanoire.fandom.com/wiki/A_Different_Kind_of_War)

# Formats

## Archive
L.A. Noire uses two archive formats, one WAD file, which is very easy to read and BIG files which are my cryptic. The archives are not encrypted in any way and the files can be easily dumped.

- https://forum.xen-tax.com/viewtopic.php@t=6623&start=360.html
- https://web.archive.org/web/20230819104229/https://forum.xentax.com/viewtopic.php?t=6623&start=195
- http://hcs64.com/vgm_ripping.html
- https://web.archive.org/web/20230817132639/https://forum.xentax.com/viewtopic.php?uid=34229&f=29&t=6797&start=0
- https://pastebin.com/MucRkpht
- https://pastebin.com/HMJhvKLS
- https://forum.xen-tax.com/viewtopic.php@t=6623&start=210.html

There are 30 game files in total:
- `animationsets.big.pc`
- `audio.big.pc`
- `cases.big.pc`
- `cases_1_1.big.pc`
- `characters.big.pc`
- `da.big.pc`
- `dlc.dlc1.big.pc`
- `dlc.dlc2.big.pc`
- `dlc.dlc3.big.pc`
- `dlc.dlc4.big.pc`
- `dlc.dlc5.big.pc`
- `dlc.dlc6.big.pc`
- `dlc.dlc7.big.pc`
- `dlc.dlc8.big.pc`
- `dlc.dlc9.big.pc`
- `movies.big.pc`
- `out.wad.pc`
- `populated.bd.big.pc`
- `populated.lowlodenv.big.pc`
- `populated.metasection.bd.big.pc`
- `populated.navmesh.dev.big.pc`
- `populated.roads.uber.dev.big.pc`
- `populated.streamingattributes.dev.big.pc`
- `props.big.pc`
- `props.high.big.pc`
- `reftextures_characters.big.pc` - file table in `out.wad.pc`
- `reftextures_populated.big.pc` - file table in `out.wad.pc`
- `shopfronts.big.pc`
- `ui_streamed_textures.big.pc`
- `vehicles.big.pc`

### WAD
A WAD file is fairly easy to read: the header is just the number of files, which is read as a chunk containing some name CRC, the offset and size for every file. At the end of the file is all the file names, as the length and then characters, which includes the directory. This gives each file the name and offset and size.

There is only one WAD file: out.wad.pc, which is odd and contains a bunch of different data.

### BIG
A BIG file is more complicated and does not contain any file names. Instead it relies on a table offset and file count to get the offset, size and name CRC and another size value. Some BIG files cannot be read this way for some reason, and instead rely on files in `out.wad.pc` which contains the file table. BIG files do not have names and rely solely on crc32 hashes which have to be guessed. Within the LANoire.exe there are many unhashed strings which have been extracted by [Baromir19](https://github.com/Baromir19/LANoireTools). However, these are lacking and there are many files where the hash can be easily guessed, but were not found when reading the exectuable.


## Files

There are many different files in the archives, some which seem random proprietary for just L.A. Noire , others which can be read directly:
- [SGES](#sges)
- [FSB4](#fsb4)
- [DGAD](#dgad)
- [TRM](#trm)
- [OGG](#ogg)
- [BINK](#bink)
- [BMF](#bmf)
- [DDS](#dds)
- [ATB](#atb)
- [FEV1](#fev1)
- [CBF1](#cbf1)
- [PTM](#ptm)
- [TRLA](#trla)
- [MPP](#mpp)
- [RNM](#rnm)

Most of the video tracks do not contain an audio track, instead relying on another audio file.

### SGES
`Segmented Compressed File - Models`
The general format for all models and images. Not much too say apart from that it seems proprietary and therefore needs more work to understand the structure. A majority of the game files are this, which presumably includes world models and images, LODs, vehicles, characters, animation data and others.

```C++
struct {
	uint16_t size; // += 0x10000 * size_coefficient
	uint8_t flags; // either 0x00, 0x10 or 0x11 - 0x01 is first chunk, 0x10 is compressed
	uint8_t size_coefficient;
} sges_chunk;

struct {
	char magic[4];
	uint16_t version; // always 7
	uint16_t num_chunks; // 1 chunk if not compressed
	uint32_t unk; // always 0

	sges_chunk chunks[num_chunks];
} sges_header;
```

### FSB4
`FMOD Sample Bank - Audio`
FSB files are proprietary but the information to read them is available. Each file can contain one or more audio tracks, which can be taken out individually and then opened using VLC.

- https://web.archive.org/web/20160622000928/https://www.fmod.org/questions/question/forum-4928/
- https://github.com/gdawg/fsbext/blob/master/src/fsb.h

### BINK
`Video`
BINK is proprietary but header information exists, as well as being openable by VLC. Not every BINK file contains an audio track.
- https://wiki.multimedia.cx/index.php/Bink_Container

### OGG
`Audio`
Not sure why this exists over FSB4, but it can be easily opened with VLC.
- https://en.wikipedia.org/wiki/Ogg
- https://fileformats.fandom.com/wiki/Ogg

### DDS
`Direct Draw Surface - Texture`
Only found in [`out.wad.pc`](#wad), presumably the rest are compressed in the [`sges`](#sges) files.
- https://learn.microsoft.com/en-us/windows/win32/direct3ddds/dx-graphics-dds-pguide#dds-file-layout

### TRM
`Trunk ? Model`
Found throughout the files, mostly in [`SGES`](#sges) files as compressed, but sometimes standalone, which contains model data including [`PTM`](#ptm) files which are possibly bones?

```C++
struct {
	uint32_t hash;
	uint32_t size;
	uint32_t offset;
} trm_entry;

struct {
	char magic[4];
	uint32_t version; // always 1
	uint32_t size1; // PTM and data files
	uint32_t size2; // VRAM files - sometimes larger than the file size
	uint32_t null; // always 0

	uint32_t num_files;
	trm_entry entries[num_files];
} trm_header;
```

Files:
- `1181384334` = `LowLODCollision`
- `3890050462` = `LowLODHierarchy`
- `2672145205` = `LowLodGraphicsMain`
- `1475192112` = `LowLodGraphicsVRAM`
- `416037040` = `MidLodGraphicsMain`
- `3496226485` = `MidLodGraphicsVRAM`
- `710690163` = `HighLodGraphicsMain`
- `3807662966` = `HighLodGraphicsVRAM`
- `1188501517` = `TextureMain`
- `2390691336` = `TextureVRAM`
- `962647487` = `UniqueTextureMain`
- `4056466362` = `UniqueTextureVRAM`
- `4236854250` = `GraphicsMain`
- `874599919` = `GraphicsVRAM`
- `388805088` = `BreakableGraphicsMain`
- `3750012901` = `BreakableGraphicsVRAM`
- `1540170686` = `Collision`
- `2306622947` = `BreakableCollision`
- `4202309806` = `Hierarchy`
- `684412659` = `BreakableHierarchy`
- `3228098164` = `Skeletons`
- `2755868908` = `BaseSkeletons`
- `2370995420` = `animation`
- `3087893650` = `AnimationSet`
- `704566783` = `SDKAnimSet`
- `586247102` = `cloth`
- `2381493261` = `?` - unknown but appears often

Vehicles:
- UniqueTextureMain
- HighLodGraphicsMain
- MidLodGraphicsMain
- LowLodGraphicsMain
- UniqueTextureVRAM
- HighLodGraphicsVRAM
- MidLodGraphicsVRAM
- LowLodGraphicsVRAM
- Collision
- Hierarchy

notebook_01.trunk.pc:
- GraphicsMain
- UniqueTextureMain
- GraphicsVRAM
- UniqueTextureVRAM
- BaseSkeletons
- 2381493261

vm_hlywd_001.trunk.pc
- GraphicsMain
- UniqueTextureMain
- GraphicsVRAM
- UniqueTextureVRAM
- 2381493261

### PTM
`PolyType Model?` ` Bones, Collisions, Hierarchy`
In most [`TRM`](#trm) files. Contains Havok file collision data with unknown header. Called `uber`?
- https://forum.xen-tax.com/viewtopic.php@t=6623&start=195.html
- https://reshax.com/topic/198-havok-middleware/
