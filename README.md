lssstools is a small collection of utilities/library functions to read
exports from LSSS

# Export file types

## BB bottom data
Export of complex sample data after pulse compression, the exported area is per ping [bottom depth - delta above, bottom depth + delta below]. 
The area is split into one or more blocks, each with constant sample distance. 
The 2D data arrays in each block is indexed as [timeIndex][rangeIndex].
Data format: http://localhost:23100/help/lsss/2.16.0/#/page/lsss/BroadbandBottomDataExport
## BB sample data
Export of complex sample data after pulse compression, for each region the rectangular bounding box in the time × range domain is exported. 
The bounding box is split into one or more blocks, each with constant sample distance. The 2D data arrays in each block is indexed as [timeIndex][rangeIndex].
Data format: http://localhost:23100/help/lsss/2.16.0/#/page/lsss/BroadbandSampleDataExport
## BB Sv(f)
Sv frequency spectra per ping from the depth ranges defined by the active regions, as displayed by the BB Sv(f) view in LSSS.
Data format: http://localhost:23100/help/lsss/2.16.0/#/page/lsss/BroadbandSvExport
Example export file: D2023006003_Svf_MESO1_School_Region_132.json
## BB TS(f)
Export of TS frequency spectra per ping for targets detected in the depth ranges defined by the active regions, as displayed by the BB TS(f) view in LSSS.
Data format: http://localhost:23100/help/lsss/2.16.0/#/page/lsss/BroadbandTsExport
## BB TS(f) tracks
Export of tracks detected by the KORONA tracking module. NB: TS is calculated using the FrequencyWindowing and FrequencyResolution configured for the BB TS(f) view. 
Only the tracks where all peak samples are contained in the selected regions are included in the export.
Data format: http://localhost:23100/help/lsss/2.16.0/#/page/lsss/BroadbandTrackExport
## Echogram plot
Export of variables selected by the Echogram plot module.
## Echosounder data
Export of the horizontally visible echosounder data to raw files. Selected regions do not limit what is exported.
## School parameters
Export of school parameters for the selected schools.
## Sv
Export of sample values in the selected regions.
## Tracks
Export of tracks detected by the KORONA tracking module. Only tracks completely contained in the selected regions are exported.
## TS
Export of TS targets detected by TS module in LSSS in the selected regions.