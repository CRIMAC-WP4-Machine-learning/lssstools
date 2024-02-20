import json
import numpy as np
import pandas as pd
# For testing only
# import matplotlib.pyplot as plt
# import xarray as xr

"""
These parsers reads the exported files from LSSS

| Authors:
|       Nils Olav Handegard <nilsolav@hi.no> 


"""


class lssstools():
    '''
    Class for reading lsss export files
    '''
    def __init__(self, jsonfile):
        with open(jsonfile) as json_file:
            data = json.load(json_file)
        self.jsonstring = data
        self.jsonfile = jsonfile
        self.exporttype = data['info']['exportType']
        
        # Check forSupported lsss export types
        lsssexporttypes = ['BroadbandSv']
        # lsssexportypes = ['BroadbandBottomData', 'BroadbandSampleData',
        #                  'BroadbandSv', 'BroadbandTs', 'BroadbandTrack']
        if self.exporttype not in lsssexporttypes:
            raise TypeError("Unsupported LSSS export data type.")

    def _Svf_to_df(self):
        Dict = {}
        # Loop over regions
        for region, _regions in enumerate(self.jsonstring['regions']):
            objectnumber = _regions['objectNumber']
            labels = _regions['labels']
            scrutiny = _regions['scrutiny']
            pings = _regions['pings']
            errorp = []
            okpings = []
            
            # Loop over pings
            for _pings in pings:
                number = _pings['number']
                time = _pings['time']
                
                # Loop over channels
                for _channel in _pings['channels']:
                    if 'error' not in set(_channel.keys()):
                        okpings.append(_pings['number'])
                        Sv = _channel['sv']
                        freq = np.linspace(_channel['minFrequency'],
                                           _channel['maxFrequency'],
                                           num=_channel['numFrequencies'])
                        N = len(freq)
                        depth = _channel['depth']
                        nominalFrequency = _channel['nominalFrequency']
                        
                        # Add data to dictionary
                        # Region
                        Dict.setdefault('region', []).extend([region]*N)
                        Dict.setdefault('labels', []).extend([labels]*N)
                        Dict.setdefault('scrutiny', []).extend([scrutiny]*N)
                        Dict.setdefault('objectnumber', []).extend(
                            [objectnumber]*N)
                        # Pings
                        Dict.setdefault('number', []).extend([number]*N)
                        Dict.setdefault('time', []).extend([time]*N)
                        # Channels
                        Dict.setdefault('depth', []).extend([depth]*N)
                        Dict.setdefault('nominalFrequency', []).extend(
                            [nominalFrequency]*N)
                        Dict.setdefault('Sv', []).extend(Sv)
                        Dict.setdefault('freq', []).extend(freq)
                        
                    # If the number os samples are to low for svf
                    else:
                        errorp.append(_pings['number'])
                        # TODO: Add Nans where no data is present
    
            df = pd.DataFrame.from_dict(Dict)
            df['time'] = pd.to_datetime(df['time'])
        return df

    def to_df(self):
        if self.exporttype == 'BroadbandSv':
            df = self._Svf_to_df()
        return df


'''
jsonfile = './testdata/D2023006003_Svf_MESO1_School_Region_132.json'
df = readSvf(jsonfile)

# Loop over region and object

df['time'] = df['time'].astype(np.int64)
dfg =  df.groupby(['region', 'objectnumber'])

for name, _dfg in dfg:
    print(name)
    _dfg = _dfg.set_index(['time','freq'])
    D = xr.Dataset.from_dataframe(_dfg)
    D['Sv'].plot()
    plt.show()
'''
