import json
import numpy as np
import pandas as pd
import xarray as xr
from tqdm import tqdm
from dateutil import parser

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
        self.chunksize = 10
        # Check for supported lsss export types
        lsssexporttypes = ['BroadbandSv', 'BroadbandTS']
        # Other datatypes not yet implemented:
        # ['BroadbandBottomData', 'BroadbandSampleData', 'BroadbandTrack']
        if self.exporttype not in lsssexporttypes:
            raise TypeError("Unsupported LSSS export data type.")

    def _Svf_to_df(self):
        # Parse the Svf data to df
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
            for _pings in tqdm(pings):
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

    def _TSf_to_df(self):
        # Parse the TSf data to df
        _js = self.jsonstring
        Dict = {}
        for j, _pings in tqdm(enumerate(_js['pings'])):
            for _channel in _pings['channels']:
                N = _channel['numFrequencies']
                for _target in _channel['targets']:
                    M = len(_target['tsc'])
                    frequency = list(np.linspace(_channel['minFrequency'],
                                                 _channel['maxFrequency'],
                                                 N))
                    Dict.setdefault('frequency',
                                    []).extend(frequency)
                    Dict.setdefault('compensated_TS',
                                    []).extend(_target['tsc'])
                    Dict.setdefault('single_target_alongship_angle',
                                    []).extend([_target['alongshipAngle']]*M)
                    Dict.setdefault('single_target_athwartship_angle',
                                    []).extend([_target['athwartshipAngle']]*M)
                    Dict.setdefault('ping_time',
                                    []).extend([
                                        parser.isoparse(_pings['time'])]*M)
                    Dict.setdefault('ping_number',
                                    []).extend([_pings['number']]*M)
                    #Dict.setdefault('single_target_identifier', []).extend([
                    #    [IDn[i]]*M)
                    Dict.setdefault('single_target_range',
                                    []).extend([_target['range']]*M)
                    Dict.setdefault('single_target_count',
                                    []).extend([N]*M)
        df = pd.DataFrame.from_dict(Dict)
        return df

    def _TSf_to_nc(self, ncfile):
        # Parse the TSf data to nc
        _js = self.jsonstring

        # Preallocate arrays for metadata
        num_targets = sum(len(_channel['targets']) for _pings in _js[
            'pings'] for _channel in _pings['channels'])
        d = _js['pings'][0]['channels'][0]
        num_freqs = d['numFrequencies']
        frequency = np.linspace(d['minFrequency'], d['maxFrequency'], d['numFrequencies'])

        single_target_alongship_angle = np.empty(num_targets, dtype=np.float32)
        single_target_athwartship_angle = np.empty(num_targets, dtype=np.float32)
        ping_time = np.zeros(num_targets, dtype=np.int64)
        ping_number = np.empty(num_targets, dtype=np.float32)
        single_target_identifier = np.empty(num_targets, dtype=np.float32)
        single_target_range = np.empty(num_targets, dtype=np.float32)
        compensated_TS = np.empty((num_targets, num_freqs), dtype=np.float32)

        target_index = 0
        for j, _pings in enumerate(tqdm(_js['pings'])):
            for _channel in _pings['channels']:
                for _target in _channel['targets']:
                    compensated_TS[target_index, :] = np.array(_target['tsc'])
                    # Assign metadata for each profile
                    single_target_alongship_angle[target_index] = _target['alongshipAngle']
                    single_target_athwartship_angle[target_index] = _target['athwartshipAngle']
                    ping_time[target_index] = np.datetime64(_pings['time']).astype(np.int64)
                    ping_number[target_index] = _pings['number']
                    single_target_identifier[target_index] = np.nan
                    single_target_range[target_index] = _target['range']
                    target_index += 1

        # Generate the xarray object
        id = [i for i in range(len(ping_number))] # The number of profiles
        coords = dict(frequency=(["frequency"], frequency), i=(["i"], id))
        dims = {'i': len(id), 'frequency': len(frequency)}

        ds = xr.Dataset(
            {
                'compensated_TS': (['i', 'frequency'], compensated_TS),
                'single_target_alongship_angle': (['i'],
                                                  single_target_alongship_angle),
                'single_target_athwartship_angle': (['i'],
                                                    single_target_athwartship_angle),
                'ping_time': (['i'], ping_time),
                'ping_number': (['i'],  ping_number),
                'single_target_range': (['i'], single_target_range),
                'single_target_identifier': (['i'], single_target_identifier)
            },
            coords=coords,
            attrs = _js['info']
        )

        # Convert attrs dictionaries to string
        for key, value in ds.attrs.items():
            if isinstance(value, dict):
                # Convert dictionary to string
                ds.attrs[key] = str(value)

        # Store to netcdf file
        ds.to_netcdf(ncfile)
    
    def to_df(self):
        if self.exporttype == 'BroadbandSv':
            df = self._Svf_to_df()
        elif self.exporttype == 'BroadbandTS':
            df = self._TSf_to_df()
        return df

    def to_nc(self, ncfile):
        if self.exporttype == 'BroadbandSv':
            raise TypeError("Unsupported NC export.")
        elif self.exporttype == 'BroadbandTS':
            df = self._TSf_to_nc(ncfile)
        return df
