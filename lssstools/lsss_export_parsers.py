import json
import numpy as np
import pandas as pd
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

    def _TSf_to_df(self):
        # Parse the TSf data to df
        _js = self.jsonstring
        Dict = {}
        for j, _pings in enumerate(_js['pings']):
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

    def to_df(self):
        if self.exporttype == 'BroadbandSv':
            df = self._Svf_to_df()
        elif self.exporttype == 'BroadbandTS':
            df = self._TSf_to_df()
        return df
