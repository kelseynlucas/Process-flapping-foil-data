# -*- coding: utf-8 -*-
"""
Created on Fri Jul 31 11:40:36 2015

@author: Kelsey



"""

def analyzeFlapperData(files):
    """
    Takes the files and associated information, and applies the methods in
    Flapper_data_analysis.py to analyze the data.
    
    Input:
    -files - an Excel spreadsheet containing information in the following
        columns:
        
        -trial - the trial name
        -testtype - (optional) - if there are test categories, ID what type here
        -name - name of the foil data combo file
        -path - folder in which the foil data combo file lives
        -pitch - ID pitch program used in the trial. Set to 1 if pitch 
            (includes 0angle) was used, 0 if heave only
        -resolve - Set to 1 if forces will need to be resolved, 0 otherwise
        -rod - set to 1 if rod data will also be analyzed
        -rodname - name of the rod data combo files
        -rodpath - filepath where the rod data combo file can be found
        -frequency - flapping frequency
        -nCycles - number of cycles of data to use in calculating net values 
            AND phase-averaging
        -SavePath - path where analyzed data should be saved
        
    Note that this code was custom-written for KL's use and reflects the
    defaults she required.
    """
    #Import useful packages
    import pandas as pd

    
    #load the file directory
    fileSet = pd.ExcelFile(files)
    fileSet = fileSet.parse('Sheet1', index_col=None)
    
    #run analysis on each trial
    for i in range(0,len(fileSet.trial)):
        
        #import foil and rod data
        dataSet = FlapperData(str(fileSet.path[i]) + '/' + str(fileSet.name[i]) + '.xls',
                         freq=fileSet.frequency[i],
                         pitch = fileSet.pitch[i],
                         rod = fileSet.rod[i],
                         rodpath = str(fileSet.rodpath[i]) + '/' + str(fileSet.rodname[i]) + '.xls'
                         )
        
        #Indicate dataSet is loaded
        print str(fileSet.trial[i]) + ' is loaded.'
        print ''
        print dataSet
        print ''
        
        #Determine if rod data will be analyzed
        r = fileSet.rod[i]
        
        #If forces need to be resolved,
        if fileSet.resolve[i] == 1:
            
            #Resolve forces
            dataSet.resolveForces(rod = r)
            
            #Filter the resolved dataset
            dataSet.filterData(cutoffFreq = 7, resolved = 1, rod = r)
            
            #If rod is included,
            if r == 1:
                
                #Subtract out the rod
                dataSet.combineWithRod(resolved = 1)
                
                #Set columns of interest for further analysis
                columns = ['Fx_noRod', 'Fy_noRod', 'Tz_noRod']
          
            #If rod is not included
            else:
                
                #Set a different set of columns of interest
                columns = ['Res_Fx_filt', 'Res_Fy_filt', 'Tz_filt']
            

            #Find and save the net values for Fx, Fy, and Tz
            dataSet.netValue(columns, 
                             fileSet.frequency[i], 
                             fileSet.nCycles[i], 
                             rod = 0,
                             save = 1,
                             filepath = str(fileSet.SavePath[i]) + '/' + str(fileSet.trial[i]) + '_netValue_resfix_' + str(fileSet.nCycles[i]) + 'reps.xlsx'
                             )

            #Find and save the phase-averaged traces for Fx, Fy, and Tz
            dataSet.phaseAvg(columns,
                             fileSet.frequency[i], 
                             fileSet.nCycles[i], 
                             str(fileSet.SavePath[i]) + '/' + str(fileSet.trial[i]) + '_phaseAvg_wstdev_resfix_' + str(fileSet.nCycles[i]) + 'reps.xlsx',
                             rod = 0
                             )

            #Save out the analyzed data
            dataSet.saveOut(str(fileSet.SavePath[i]) + '/' + str(fileSet.trial[i]) + '_resfix.xlsx',
                            rod = r,
                            rodpath = str(fileSet.SavePath[i]) + '/rod/' + str(fileSet.trial[i]) + '_resfix_rod.xlsx'
                            )

        #if forces do not need to be resolved:
        else:    
            
            #Filter unresolved data
            dataSet.filterData(cutoffFreq = 7, resolved = 0, rod = r)
            
            #If rod is included,
            if r == 1:
                
                #Subtract out the rod
                dataSet.combineWithRod(resolved = 0)
                
                #Set columns of interest for further analysis
                columns = ['Fx_noRod', 'Fy_noRod', 'Tz_noRod']
            
            #if rod is not included,
            else:
                
                #Set a different set of columns of interest
                columns = ['Fx_filt', 'Fy_filt', 'Tz_filt']

            #Find and save the net values for Fx, Fy, and Tz
            dataSet.netValue(columns, 
                             fileSet.frequency[i], 
                             fileSet.nCycles[i], 
                             rod = 0,
                             save = 1,
                             filepath = str(fileSet.SavePath[i]) + '/' + str(fileSet.trial[i]) + '_netValue_resfix_' + str(fileSet.nCycles[i]) + 'reps.xlsx'
                             )

            #Find and save the phase-averaged traces for Fx, Fy, and Tz
            dataSet.phaseAvg(columns,
                             fileSet.frequency[i], 
                             fileSet.nCycles[i], 
                             str(fileSet.SavePath[i]) + '/' + str(fileSet.trial[i]) + '_phaseAvg_wstdev_resfix_' + str(fileSet.nCycles[i]) + 'reps.xlsx',
                             rod = 0
                             )

            #Save out the analyzed data
            dataSet.saveOut(str(fileSet.SavePath[i]) + '/' + str(fileSet.trial[i]) + '_resfix.xlsx',
                            rod = r,
                            rodpath = str(fileSet.SavePath[i]) + '/rod/' + str(fileSet.trial[i]) + '_resfix_rod.xlsx'
                            )

        #Indicate set done and current progress
        print 'Completed ' + str(fileSet.trial[i])
        print str(i+1) + ' of ' + str(len(fileSet.trial)) + ' sets complete.'
        print ''