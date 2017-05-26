# -*- coding: utf-8 -*-
"""
Created on Wed Jul 29 11:23:27 2015

@author: Kelsey Lucas



"""

class FlapperData(object):
    """
    Load Flapper data as this class type to perform data analysis.
    
    Inputs:
        foil - (str) filepath and name for foil combo file
        
        pitch - default is 0 (False - a heave only program was used).  Set to
            1 (True) if pitch, including 0angle, was applied.
            
        rod - default is 0 (False - do not load rod data).  Set to 1 (True)
            to load corresponding rod-only combo file, if subtraction of rod
            data is needed.
        
        rodpath - set to the filepath and name of the rod combo file when
            rod = 1
            
            
    The methods associated with Flapper Data objects can be used to:
        -resolve forces
        -filter data
        -subtract rod contributions
        -plot time traces of data
        -find phase-averaged forces/torques
        -find net force/torque over one or more complete motion cycles
        
    """
    
    def __init__(self, foil, freq, pitch=0, rod=0, rodpath='none'):
        """
        Tells Python what to do when Flapper data is loaded
        """
        
        #Load some useful packages - Pandas, Numpy, MatPlotLib, and Math
        import pandas as pd
        import numpy as np
        
        #Set up dataframe (table) displays
        pd.set_option('display.width', 500)
        pd.set_option('display.max_columns', 100)
        
        #Load the foil data to a dataframe
        self.foilData = pd.read_csv(foil,delimiter='\t')
        
        #Get rid of columns that don't show force, torque, or position data
        self.foilData = self.foilData.drop(['Pressure 1 Ai2',
                                            'Pressure 2 Ai3',
                                            'Pressure 3 Ai4',
                                            'Pressure 4 Ai5',
                                            'digital in loop start 6221',
                                            'camera trigger echo 6221',
                                            'Loop Pulse'],
                                            axis=1)
        
        #Give the dataframe columns names
        self.foilData = self.foilData.rename(columns = {'X axis encoder 6602 degrees':'pitch_pos',
                                                        'Y axis encoder 6602 meters':'heave_pos',
                                                        'Fx (N)':'Fx',
                                                        'Fy (N)':'Fy',
                                                        'Fz (N)':'Fz',
                                                        'Tx (N-mm)':'Tx',
                                                        'Ty (N-mm)':'Ty',
                                                        'Tz (N-mm)':'Tz'
                                                        })
                                                        
        #Add a time column
        self.foilData['time']=np.linspace(0, 9.999, num=10000)
        
        #Set pitch to 0 degrees in heave only datasets
        if pitch == 0:
            self.foilData['pitch_pos'] = 0.
        
        #Center pitch_pos and heave_pos on the x-axis by subtracting the mean
        #from each data point
        isEven = 10. % freq
        if isEven == 0:
            self.foilData['heave_pos']=self.foilData['heave_pos'] - self.foilData.heave_pos.mean()
        elif freq == 0:
            self.foilData['heave_pos']= 0.
        else:
            last = int(1000.*freq*int(10./freq))
            heave_avg = np.mean(self.foilData['heave_pos'][0:last])
            self.foilData['heave_pos']=self.foilData['heave_pos'] - heave_avg
        
        if pitch == 1:
            self.foilData['pitch_pos']=self.foilData['pitch_pos'] - self.foilData.pitch_pos.mean()
            
            
        
        #Optionally load rod data and set up the same type of dataframe.
        if rod == 1: 
            #Load the foil data to a dataframe
            self.rodData = pd.read_csv(rodpath,delimiter='\t')
            
            #Get rid of columns that don't show force, torque, or position data
            self.rodData = self.rodData.drop(['Pressure 1 Ai2',
                                            'Pressure 2 Ai3',
                                            'Pressure 3 Ai4',
                                            'Pressure 4 Ai5',
                                            'digital in loop start 6221',
                                            'camera trigger echo 6221',
                                            'Loop Pulse'],
                                            axis=1)
            
            #Give the dataframe columns names
            self.rodData = self.rodData.rename(columns = {'X axis encoder 6602 degrees':'pitch_pos',
                                                            'Y axis encoder 6602 meters':'heave_pos',
                                                            'Fx (N)':'Fx',
                                                            'Fy (N)':'Fy',
                                                            'Fz (N)':'Fz',
                                                            'Tx (N-mm)':'Tx',
                                                            'Ty (N-mm)':'Ty',
                                                            'Tz (N-mm)':'Tz'
                                                            })
                                                            
            #Add a time column
            self.rodData['time']=np.linspace(0, 0.9999, num=10000)
            
            #Set pitch to 0 degrees in heave only datasets
            if pitch == 0:
                self.rodData['pitch_pos'] = 0.
            
            #Center pitch_pos and heave_pos on the x-axis by subtracting the mean
            #from each data point
            isEven = 10. % freq
            if isEven == 0:
                self.rodData['heave_pos']=self.rodData['heave_pos'] - self.rodData.heave_pos.mean()
            elif freq == 0:
                self.rodData['heave_pos']= 0.
            else:
                last = int(1000.*freq*int(10./freq))
                heave_avg = np.mean(self.rodData['heave_pos'][0:last])
                self.rodData['heave_pos']=self.rodData['heave_pos'] - heave_avg
            
            if pitch == 1:
                self.rodData['pitch_pos']=self.rodData['pitch_pos'] - self.rodData.pitch_pos.mean()
                
    
    
    
    def __str__(self):
        """
        Displays which data sets have been loaded.
        """
        
        #Set up text to display
        outcome = 'foilData has ' +str(self.foilData.shape[0])+ ' data points in ' +str(self.foilData.shape[1])+ ' columns:' +str(list(self.foilData.columns))
        
        #If rod data was also loaded,
        try:
            #Set text to display about rod
            rod_outcome = '  rodData also loaded with ' +str(self.rodData.shape[0])+ ' data points in ' +str(self.rodData.shape[1])+ ' columns.'
            #Set the whole text to display            
            outcome += rod_outcome
            #Display text
            return outcome
        #Otherwise, just display foil text
        except:
             return outcome
             
    
    
    def resolveForces(self, rod=0):
        """
        Resolves forces collected during pitch programs - with a rotating
        force-torque sensor - to upstream (Fx) and lateral (Fy) components.
        Reports data in new columns Res_Fx and Res_Fy
        
        Input:
        -rod - default is 0 (False - do not load rod data).  Set to 1 (True)
            to load corresponding rod-only combo file, if subtraction of rod
            data is needed.
            
        """
        def resolve_forces(df):
            """"
            A helper-code that performs the resolve Fx and Fy calculation:
            
            Res_Fx = Fx*cos(pitch_pos) + Fy*sin(pitch_pos)
            Res_Fy = -Fx*sin(pitch_pos) - Fy*cos(pitch_pos)
            
            Note that pitch_pos is converted to radians from degrees before
            calculation.
            
            """
            #load a package            
            import numpy as np
            
            #Resolve Fx = Fx*cos(pitch)+Fy*sin(pitch)
            df['Res_Fx']=df.Fx*np.cos(np.radians(df.pitch_pos))+df.Fy*np.sin(np.radians(df.pitch_pos))
            #Resolve Fy = -Fx*sin(pitch)-Fy*cos(pitch)
            #df['Res_Fy']=-(df.Fx*np.sin(np.radians(df.pitch_pos)))-df.Fy*np.cos(np.radians(df.pitch_pos))
            df['Res_Fy']=-(df.Fx*np.sin(np.radians(df.pitch_pos)))+df.Fy*np.cos(np.radians(df.pitch_pos))
            return df
            
        #Resolve forces and insert into the dataframe
        self.foilData = resolve_forces(self.foilData)
        
        #If rod data is provided, repeat for the rod data.
        if rod == 1:
            self.rodData = resolve_forces(self.rodData)
        
    
    def filterData(self, cutoffFreq=10, resolved=0, rod=0):
        """
        Applies a low-pass Butterworth filter to Flapper data & inserts 
        filtered data into new columns Fx_filt (or Res_Fx_filt),
            Fy_filt (or Res_Fy_filt), and Tz_filt
        
        Operates on Fx (or Res_Fx), Fy (or Res_Fy), and Tz
        
        Input:
        
        -cutoffFreq - default is 10 Hz.  Set to other values as needed
            to produce smooth traces.
        
        -resolved - default is 0 (False - forces have not been resolved).  Set
            to 1 if Fx and Fy were resolved.
            
        -rod - default is 0 (False - do not load rod data).  Set to 1 (True)
            to load corresponding rod-only combo file, if subtraction of rod
            data is needed.
            
        """
        #Load filtering functions
        from scipy.signal import butter, filtfilt

        def apply_filter(df):
            """
            A helper-code that applies a Butterworth filter to the Flapper data
            & inserts results into new columns
            
            Applies the Butterworth filter in 2 pass - at a fraction of the 
            cut-off frequency each time - to eliminate phase-shifts from the 
            outcome.
            """
            
            #C is a proprotionality factor by which the desired cutoff 
            #frequency will be adjusted to account for multiple passes.
            #C = 0.802 for n=2 passes, calculated by:
            # C = (2^(1/n)-1)^(1/4)
            
            C = 0.802
            
            #Create filter operation
            #'1000/2' is the Nyquist frequency, or half of the sampling frequency
            b, a = butter(2, (cutoffFreq/C)/(1000/2), btype = 'low')
            
            #Apply the filter
            if resolved == 0:
                df['Fx_filt'] = filtfilt(b, a, df.Fx)
                df['Fy_filt'] = filtfilt(b, a, df.Fy)
                df['Tz_filt'] = filtfilt(b, a, df.Tz)
            
            #Apply the filter instead to the resolved forces, if available.
            else:
                df['Res_Fx_filt'] = filtfilt(b, a, df.Res_Fx)
                df['Res_Fy_filt'] = filtfilt(b, a, df.Res_Fy)
                df['Tz_filt'] = filtfilt(b, a, df.Tz)
            
            return df
            
        #Filter foil data
        self.foilData = apply_filter(self.foilData)
        
        #If rod data are available, filter the rod data
        if rod == 1:
            self.rodData = apply_filter(self.rodData)
            
        
    def simplePlot(self, x, y):
        """
        Quick, basic plot of y over x to view data.  Not meant for 
        figure-making.
        """
        #load plot-making package        
        import matplotlib.pyplot as plt
        
        #create a simple plot
        plt.plot(x,y)
        
    
    def combineWithRod(self, resolved=0):
        """
        Subtracts rod data from foil data to eliminate the contribution of 
        the rod & reports results in new columns Fx_noRod, Fy_noRod,
        and Tz_noRod.
        
        Applies to filtered data only.
        
        Input:
        -resolved - default = 0 (False - forces were not resolved).  Set equal
            to 1 if forces have been resolved.
        
        """
        
        #Find the first heave position in the foil data.
        firstHeave = self.foilData.heave_pos[0]
        
        #Find out if heave is decreasing or increasing by comparing to next
        #heave position.
        if firstHeave < self.foilData.heave_pos[1]:
            direction = 'incr'
        else:
            direction = 'decr'
        
        #initialize an index to let us note where we are in rod data (below)
        i=0
        
        #Read each heave position in the rod data, one at a time.
        for heave in self.rodData.heave_pos:
        
        #If heave position in the rod data matches the one noted from foil data
        #(Because different passes of the Flapper rarely are identical in
        #position reports, allow for error of 0.00005 m.)
            if firstHeave - heave < 0.00005:
            
                #Determine if heave is increasing or decreasing at the first
                #occurance by comparing to the next heave position.
                try:
                    if heave < self.rodData.heave_pos[i+1]:
                        rDirection = 'incr'
                    else:
                        rDirection = 'decr'
                
                #If the matching heave occurs at the end of the list of heave 
                #positions, check for incr/decr using the previous value instead
                except:
                    if heave < self.rodData.heave_pos[i-1]:
                        rDirection = 'decr'
                    else:
                        rDirection = 'incr'
            
                #if direction of motion matches,
                if direction == rDirection:
                    
                    #note the index in rod where this happens.
                    matchIndex = i
                
                    #break out of loop
                    break
                
                #else, continue searching for the next appearance of that heave
                #position in the rod data.
            
            #increment i
            i+=1
            
        #initialize storage for corrected data
        newFx = []
        newFy = []
        newTz = []
        
        #initialize index to go through rod data row-by-row
        j=matchIndex
        
        
        
        #going line by line, starting at the beginning of foil data and
        #the noted index from rod data (corresponding points)
        for index in range(0,self.foilData.shape[0]):
        
            if resolved == 0:
            
                try:
                    
                    #subtract the rod Fx, Fy, and Tz (filtered) from the foil
                    newFx.append(self.foilData.Fx_filt[index] - self.rodData.Fx_filt[j])
                    newFy.append(self.foilData.Fy_filt[index] - self.rodData.Fy_filt[j])
                    newTz.append(self.foilData.Tz_filt[index] - self.rodData.Tz_filt[j])
        
                #when we run out rows in the rod data,
                except:
        
                    #start at the beginning of the rod data
                    j=0
                    newFx.append(self.foilData.Fx_filt[index] - self.rodData.Fx_filt[j])
                    newFy.append(self.foilData.Fy_filt[index] - self.rodData.Fy_filt[j])
                    newTz.append(self.foilData.Tz_filt[index] - self.rodData.Tz_filt[j])
                
                #and continue to next row
                j+=1
        
            else:
            
                try:
                    
                    #subtract the rod Fx, Fy, and Tz (filtered) from the foil
                    newFx.append(self.foilData.Res_Fx_filt[index] - self.rodData.Res_Fx_filt[j])
                    newFy.append(self.foilData.Res_Fy_filt[index] - self.rodData.Res_Fy_filt[j])
                    newTz.append(self.foilData.Tz_filt[index] - self.rodData.Tz_filt[j])
        
                #when we run out rows in the rod data,
                except:
                    #start at the beginning of the rod data
                    j=0
                    newFx.append(self.foilData.Res_Fx_filt[index] - self.rodData.Res_Fx_filt[j])
                    newFy.append(self.foilData.Res_Fy_filt[index] - self.rodData.Res_Fy_filt[j])
                    newTz.append(self.foilData.Tz_filt[index] - self.rodData.Tz_filt[j])
                
                #and continue to next row
                j+=1
          
        #add the corrected data to the foil dataframe
        self.foilData['Fx_noRod']=newFx
        self.foilData['Fy_noRod']=newFy
        self.foilData['Tz_noRod']=newTz
        
        
    
    def netValue(self, columns, freq, nCycles, rod=0, save=0, filepath='none'):
        """
        Finds the net (time-averaged) value of data columns over
        the first n cycles.
        
        Input:
        
        -columns - a list of data to calculate averages for
            Ex: [Res_Fx_filt, heave_pos]
            
        -freq - flapping frequency used
        
        -nCycles - the number of cycles to take the average over.  Must
            be at least 1, and no more than 10 seconds worth of time.
            
        -rod - if average values for the rod are also desired, set equal to 1
        
        -save - set to 1 to save net values to an Excel file.
        
        -filepath - when save == 1, set equal to the filepath where net
            values should be saved
        
        """
        #So don't divide by zero in static case (0 Hz)
        if freq == 0:
            print 'Static case.  Finding net values by averaging over ' +str(nCycles) + ' subsets of time trace.'
            print ''
            p = 1./nCycles
        
        else:
            #find period of motion cycle in s
            p = 1./freq
        
        #convert to ms
        p *=1000
        #p equals the number of dataframe rows per 1 motion cycle
        
        #find total number of rows for nCycles
        p *= nCycles
        
        #round p to an integer
        p = int(round(p))
        
        #Create a dictionary to store averages in
        avgs = {}
        
        #for each column to calculate an average for:
        for col in columns:
            
            #Find the average of the first p rows of the column
            a = self.foilData[col][0:p].mean()
            
            #add it to the dictionary
            avgs[col]= [a]
        
        #if rod data is desired too
        if rod == 1:
            
            #do the same thing for the rod data
            
            #for each column to calculate an average for:
            for col in columns:
                
                #Find the average of the first p rows of the column
                a = self.rodData[col][0:p].mean()
                
                #add it to the dictionary
                avgs[col+'_rod'] = [a]
                
        #optionally save the net values
        if save == 1:
            
            #save to the filepath
            
            #import the dataframe-making package
            import pandas as pd
            
            #convert dictionary to a dataframe
            avgs=pd.DataFrame(avgs, columns=avgs.keys())
            
            #save to an excel file
            avgs.to_excel(filepath)
            
            #confirm done
            print 'Saved file as ' + filepath.split('/')[-1]
        
        #deliver the averages
        return avgs
        
    
    def saveOut(self, filepath, rod=0, rodpath='none'):
        """
        Save out dataframe to Excel at the given filepath.
        
        Inputs:
        
        -filepath - including file name; where to save file
        
        -rod - set equal to 1 to also save out the rod dataframe; otherwise,
            only save out foil data
        
        -rodpath - if rod == 1, fill in desired filepath and name
            
        """
        #save foil data
        self.foilData.to_excel(filepath)
        print 'Foil data saved'
        
        #optionally save rod data
        if rod == 1:
            self.rodData.to_excel(rodpath)
            print 'Rod data saved'
            
    
    def phaseAvg(self, columns, freq, nCycles, filepath, rod=0):
        """
        Phase averages data in columns over nCycles.
        
        Input:
        
        -columns - a list of data to calculate averages for
            Ex: [Res_Fx_filt, heave_pos]
            
        -freq - flapping frequency used
        
        -nCycles - the number of cycles to take the average over.  Must
            be at least 1, and no more than 10 seconds worth of time.
            
        -filepath - where to save phase-averaged data
            
        -rod - if average values for the rod are also desired, set equal to 1
        
        """
        
        import numpy as np        
        
        #So don't divide by zero in static case (0 Hz)
        if freq == 0:
            print 'Static case.  Phase-averaging over ' +str(nCycles) + ' subsets of time trace.'
            print ''
            #p is the number of dataframe rows in 1 motion cycle.  In static case,
            #break video into 1000-frame chunks
            p = 1000
        
        else:
            #find period of motion cycle in s
            p = 1./freq
        
            #convert to ms
            p *= 1000
            #p equals the number of dataframe rows per 1 motion cycle
            
            #round p to an integer
            p = int(round(p))
        
        #Create a dictionary to store averages in
        avgs = {}
        
        #for each column to calculate an average for:
        for col in columns:
            
            #make a list of the each time-point's phase-average and standard deviation
            averageList = []            
            stdevList = []
            
            #look at the ith row in a cycle
            for i in range(0,p):
                
                #initialize storage for the sum of corresponding values
                total = 0
                #make a list of the values
                values = []
                
                #look at the ith row in the nth cycle (all in turn)
                for n in range(0, nCycles):
                    
                    #Get the value in the ith row of the nth cycle
                    total += self.foilData[col][i+n*p]
                
                    #Get the values themselves
                    values.append(self.foilData[col][i+n*p])
                
                #divide by nCycles to get the average for that time point
                newAvg = total/nCycles
                
                #add the average to the collection
                averageList.append(newAvg)
                
                #make a list of square errors
                sqerrors = []
                
                #calculate the standard deviation
                for v in values:
                    sqerrors.append(abs(v-newAvg)**2.)
                sumsqerrors = np.sum(sqerrors)
                stdev = np.sqrt(sumsqerrors/2.)
                
                #add standard deviation to the list
                stdevList.append(stdev)                
                
            #add the phased-average column to the dictionary    
            avgs[col] = averageList
            #add the error column to the dictionary
            avgs[(col+'_std')] = stdevList
        
        #make a time sequence
        time = np.array(range(0,p))
        time = time/1000.
        avgs['time']=time
        
        if rod == 1:
            #for each column to calculate an average for:
            for col in columns:
                
                #make a list of the each time-point's phase-average
                averageList = []            
                
                #look at the ith row in a cycle
                for i in range(0,p):
                    
                    #initialize storage for the sum of corresponding values
                    total = 0
                    
                    #look at the ith row in the nth cycle (all in turn)
                    for n in range(0, nCycles):
                        
                        #Get the value in the ith row of the nth cycle
                        total += self.rodData[col][i+n*p]
                        
                        #Get the values themselves
                        values.append(self.rodData[col][i+n*p])
                
                    
                    #divide by nCycles to get the average for that time point
                    newAvg = total/nCycles
                    
                    #add the average to the collection
                    averageList.append(newAvg)
                    
                    #make a list of square errors
                    sqerrors = []
                
                    #calculate the standard deviation
                    for v in values:
                        sqerrors.append(abs(v-newAvg)**2.)
                    sumsqerrors = np.sum(sqerrors)
                    stdev = np.sqrt(sumsqerrors/2.)
                
                    #add standard deviation to the list
                    stdevList.append(stdev)
                    
                #add the phase-averaged column to the dictionary    
                avgs[col+'_rod'] = averageList
                #add the error column to the dictionary
                avgs[(col+'_rod_std')] = stdevList
                
        #save the dictionary to filepath
            
        #import the dataframe-making package
        import pandas as pd
            
        #convert dictionary to a dataframe
        avgs=pd.DataFrame(avgs, columns=avgs.keys())
            
        #save to an excel file
        avgs.to_excel(filepath)
            
        #confirm done
        print 'Saved file as ' + filepath.split('/')[-1]
        