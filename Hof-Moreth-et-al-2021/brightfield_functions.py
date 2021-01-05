import numpy as np
import matplotlib.pyplot as plt
import os
import glob
from pandas import DataFrame, read_csv, ExcelWriter, to_numeric, Series
import math
from scipy import stats
 
NumTimeSteps_Loss = 1
 
def read_data(folder, interval, start):
    """
    read_data(folder, interval, start)
        loads experimental data of the format .csv to the program
    
        Parameters
        ----------
            folder: string
            interval: string
            start: float
        
        Returns
        -------
            time : array_like
                    list of analysed timepoints
            size : array_like     
                    list of values for the size of the organoids for each analysed time point
            circularity : array_like
                    list of values for the circularity of the organoids for each analysed time point
        
        Examples
        --------
            >>> t, s, c = functions.read_data('./', '2', 1)
    """
    os.chdir(folder)
    extension = 'csv'
    iv = float(interval)
    fileList = [i for i in glob.glob('*.{}'.format(extension))]
    timepoints = len(fileList)
    tresh = timepoints//2
    endTime = timepoints*iv+start
    time = np.arange(start, endTime, iv)
    time.tolist()
    size = DataFrame(columns=time)
    circularity = DataFrame(columns=time)
    for f in fileList:
        tp = f.split("-")
        timepoint = int(tp[0])
        try:
            csv = read_csv(f, error_bad_lines=False)
            rows = len(csv.iloc[:, 1])
            for i in range(0, rows):
                Label = csv.iloc[i, 1]
                Area = csv.iloc[i, 2]
                size.set_value(Label, timepoint, Area)
                Circularity = csv.iloc[i, 4]
                circularity.set_value(Label, timepoint, Circularity)
        except:
            Label = 'no data'
            Area = 'no data'
            Circularity = 'no data'
            size.set_value(Label, timepoint, Area)
            circularity.set_value(Label, timepoint, Circularity)
    size = size.reindex(sorted(size.columns), axis=1)
    size = size.dropna(axis=1, how='all')
    size = size.dropna(axis=0, how='any', thresh=tresh)  
    circularity = circularity.reindex(sorted(size.columns), axis=1)
    circularity = circularity.dropna(axis=1, how='all')
    circularity = circularity.dropna(axis=0, how='any', thresh=tresh)
    circularity_matrix = circularity.values.tolist()
    organoids = circularity.index.values.tolist()
    for c in circularity_matrix:
        b2 = circularity_matrix.index(c)
        for v in range(0, len(c)):
            if c[v] < 0.6:
                a = v
                b = organoids[b2]
                size = size.set_value(b, a, np.NaN)
    for col in size:
        size[col] = to_numeric(size[col], errors='coerce')
    size = size.interpolate(method='linear', axis=1, limit=2)
    if len(size.columns) > 1:
        size.drop(size.columns[len(size.columns)-1], axis=1, inplace=True)
    size_matrix = size.values.tolist()
    for r in range(0, len(size_matrix)):
        nan = 0
        ev = 0
        sv = 0
        for v in range(0, len(size_matrix[r])):
            x = size_matrix[r]
            z = x[v]
            if math.isnan(z) == False:
                if nan == 0:
                   sv = v
                   ev = v
                   nan = 1
                else:
                    ev = v+1
            else:
                if ev == 0:
                    continue
                nan = 0
                if ev - sv < 15:
                    for i in range(sv, ev+1):
                        b = organoids[r]
                        size.set_value(b, i, np.NaN)
    size = size.dropna(axis=0, how='any', thresh=tresh)
    size = size.dropna(axis=1, how='all')
    return time, size, circularity
   
 
def moving_average(a_list, frame):
    """
    moving_average(a_list, frame)
        performes a moving average smoothing on a given list of values
    
        Parameters
        ----------
            a_list: array_like
                    list of values to smooth
            frame: integer
                    size of the smoothing window
            
        Returns
        -------
            smoothed : array_like
                    smoothend list of values 
            
        Examples
        --------
            >>> s = functions.moving_average([1., 2., 3., 4., 5.], 3)
    """
    l = len(a_list)
    smoothed = []
    if frame == 0:
        print('zero is not a valid input')
        return a_list
    elif frame == 1:
        return a_list
    else:
        if frame % 2 == 0 and frame != 0:
            f = int(frame/2)
            for v in range(1, f):
                last = v+f-2
                average = sum(a_list[0:last])/len(a_list[0:last])
                smoothed.append(average)
            for v in range(f, l-f):
                first = v-f
                last = v+f
                average = sum(a_list[first:last])/len(a_list[first:last])
                smoothed.append(average)
            for v in range(l-f, l+1):
                first = v-f
                average = sum(a_list[first:l])/len(a_list[first:l])
                smoothed.append(average)
        else:
            f = int(frame/2-0.5)
            for v in range(1, f):
                last = v+f-2
                average = sum(a_list[0:last])/len(a_list[0:last])
                smoothed.append(average)
            for v in range(f, l-f):
                first = v-f
                last = v+f+1
                average = sum(a_list[first:last])/len(a_list[first:last])
                smoothed.append(average)
            for v in range(l-f, l+1):
                first = v-f
                average = sum(a_list[first:l])/len(a_list[first:l])
                smoothed.append(average)
        return smoothed
 
 
def calculate_derivative(x_vector, y_vector):
    """
    calculate_derivative(x_vector, y_vector)
        determines the derivative of y (values) with respect to x (time)

        Parameters
        ----------
            x_vector : array_like
                    list of values (organoid size)
            y_vector : array_like
                    list of values (time)
            
        Returns
        -------
            derivative : array_like
                    list of values with the gradient at each x (time)    
    """
    derivative = []
    for i in range(1, len(x_vector)):
        delta_x = x_vector[i]-x_vector[i-1]
        delta_y = y_vector[i]-y_vector[i-1]
        v_derivative = delta_y/delta_x
        derivative.append(v_derivative)
    return derivative
 
def find_turning_points(x_vector, y_vector, limit = 0):
    """
    find_turning_points(x_vector, y_vector, limit = 0)
        detects turing points in the given data
        
        Parameters
        ----------
            x_vector : array_like
                    list of values (organoid size)
            y_vector : array_like
                    list of values (time)
            limit : float
                    pass
                    DEFAULT (0)
            
        Returns
        -------
            tp : integer
                    count of turing points in the given x_array
    """
    tp = 1
    derivative = calculate_derivative(x_vector, y_vector)
    r1 = np.corrcoef(x_vector, y_vector).min()
    mi = derivative.index(min(derivative))
    if 2 < mi < len(x_vector) - 2:
        a = mi - 2
        b = mi + 2
        x_frame = np.asarray(x_vector[a:b])
        y_frame = np.asarray(y_vector[a:b])
        fit = np.polyfit(x_frame, y_frame, 1)
    elif mi <= 2:
        a = mi
        b = mi + 4
        x_frame = np.asarray(x_vector[a:b])
        y_frame = np.asarray(y_vector[a:b])
        fit = np.polyfit(x_frame, y_frame, 1)
    else:
        a = mi - 4
        b = mi
        x_frame = np.asarray(x_vector[a:b])
        y_frame = np.asarray(y_vector[a:b])
        fit = np.polyfit(x_frame, y_frame, 1)
    ma = derivative.index(max(derivative))
    if 2 < ma < len(x_vector) - 2:
        a = ma - 2
        b = ma + 2
        x_frame = np.asarray(x_vector[a:b])
        y_frame = np.asarray(y_vector[a:b])
        fit2 = np.polyfit(x_frame, y_frame, 1)
    elif ma <= 2:
        a = ma
        b = ma + 4
        x_frame = np.asarray(x_vector[a:b])
        y_frame = np.asarray(y_vector[a:b])
        fit2 = np.polyfit(x_frame, y_frame, 1)
    else:
        a = ma - 4
        b = ma
        x_frame = np.asarray(x_vector[a:b])
        y_frame = np.asarray(y_vector[a:b])
        fit2 = np.polyfit(x_frame, y_frame, 1)
    intersection_x = (fit[1]-fit2[1])/(fit[0]-fit2[0])
    if intersection_x < 0:
        ix = intersection_x * -1
    else:
        ix = intersection_x
    ints = 0
    for i in range(1, len(x_vector)):
        if x_vector[i-1] <= ix <= x_vector[i]:
            ints = i
    if 0 < ints < len(x_vector):
        r2 = np.corrcoef(x_vector[0:ints], y_vector[0:ints]).min()
        r3 = np.corrcoef(x_vector[ints:-1], y_vector[ints:-1]).min()
        if r2 >= r1-limit or r3 >= r1-limit:
            tp = ints
        else:
            tp = 1
    return tp
 
   
def find_collapse(x_vector, y_vector, limit, collapse_track = False, NumTimeSteps_Gain = 1):
    """
    find_collapse(x_vector, y_vector, limit, collapse_track = False)
        Detects collapse events during organoid growth. 
        A collapse event starts if on NumTimeSteps_Gain subsequent time steps the size of the organoid is reduced by limit percent.
        The end of a collapse event is reached as soon as the size of the organoid increases after a collapse event is detected.
        
        Parameters
        ----------
            x_vector : array_like
                    list of values (organoid size)
            y_vector : array_like
                    list of values (time)
            limit : float
                    gives the minimum required size reduction of an organoid for a detectable collapse event
            collapse_track : boolean
                    determines whether the end_collapse array is returned to the main program 
                    DEFAULT (False)
            NimTimeSteps_Gain : integer 
                    determines the number of subsequent time steps of size reduction for a detectable collapse event
                    DEFAULT (1)
            
        Returns
        -------
            collapse : array_like
                    list of values which contains the time points of all detected collapse events
            end_collapse : array_like (optional)
                    list of values which contains the time points of all detected collapse end events
        
        Examples
        --------
            >>> collapse_start, collapse_end = functions.find_collapse(size_data, time_data, 5, True, 1)
    """
    collapse = []
    end_collapse = []
    
    double = 0
    for i in range(max(NumTimeSteps_Loss, NumTimeSteps_Gain), len(x_vector)-1):
        NetLoss = True
        NetGain = True
       
        for j in range(i-NumTimeSteps_Loss, i):
            value_low  = y_vector[j]-(y_vector[j] / 100 * limit)
            NetLoss = NetLoss and (y_vector[j+1] < value_low)
           
        for j in range(i-NumTimeSteps_Gain, i):
            NetGain = NetGain and (y_vector[j+1] > y_vector[j])
           
        if double == 0 and NetLoss:
            collapse.append(i-NumTimeSteps_Loss)
            double = 1
        elif double == 1 and NetGain:
            end_collapse.append(i-NumTimeSteps_Gain)
            double = 0
       
    if collapse_track:
        return collapse, end_collapse
    else:
        return collapse
   
def phase_characterization(x_vector, y_vector, collapse, collapse_end):
    """
    phase_characterization(x_vactor, y_vector, collapse, collapse_end)

        Parameters
        ----------
            x_vector : array_like
                    list of values (organoid size)
            y_vector : array_like
                    list of values (time)
            collapse : array_like
                    list of values (begin of collapse events)
            collapse_end : array_like
                    list of values (end of collapse events)
        Returns
        -------
            phases : array_like
            
        Examples
        --------
            >>> functions.phase_characterization(size_data, time_data, collapse_begin, collapse_end)
    """
    smoothed = moving_average(y_vector, 5)
    
    phases = []
    extreme_points = collapse
   
    for i in collapse_end:
        extreme_points.append(i)
       
    extreme_points.append(0)
    extreme_points.append(len(x_vector))
    derivative = calculate_derivative(x_vector, smoothed)
    for i in range(1, len(derivative)):
        if derivative[i] < -0.01 and derivative[i-1] > 0.01:
            extreme_points.append(i)
        elif derivative[i] > 0.01 and derivative[i-1] < -0.01:
            extreme_points.append(i)
    extreme_points = sorted(set(extreme_points))
   
    for i in range(0, len(extreme_points)-1):
        if extreme_points[i+1] - extreme_points[i] > 10:
            a = extreme_points[i]
            b = extreme_points[i+1]
            turning_point = find_turning_points(x_vector[a:b], smoothed[a:b], 0)
            if not turning_point == 1:
                ep = extreme_points[i] + turning_point
                extreme_points.append(ep)
    extreme_points = sorted(set(extreme_points))
   
    for i in range(0, len(extreme_points)-1):
        a = extreme_points[i]+1
        b = extreme_points[i+1]-1
        r = np.corrcoef(x_vector[a:b], y_vector[a:b]).min()
 
        if r > 0.0 and b - a >= 5:
            fit = np.polyfit(x_vector[a:b], y_vector[a:b], 1)
            data = [a, b, fit[0], r]
            phases.append(data)
           
    return phases
 
def create_plot(matrix, time, figname, title, ymin, ymax):
    """
    create_plot(matrix, time, figname, title, ymin, ymax)
        Creates a plot of the given data.
        
        Parameters
        ----------
            matrix : array_like
                    list of values (organoid size)
            time : array_like
                    list of values (time)
            figname : string
                    name of the saved image
            title : string
                    title of the figure
            ymin : float
                    ymin limit for the axis
            ymax : float
                    ymax limit for the axis
    """
    striped = []
    for j in range(0, len(matrix)):
        short = [x for x in matrix[j] if str(x) != 'nan']
        vec = matrix[j]
        r_vec = [x / short[5] for x in vec]
        start = 0
        for i in range(0, len(r_vec)+1):
            if math.isnan(vec [i]) == False:
                start = i
                vec2 = r_vec[start:]
                break
        while len(vec2) < len(matrix[0]):
            vec2.append(np.nan)
        striped.append(vec2) 
    data = np.array(striped)
    np.set_printoptions(threshold=np.inf)
    average = np.nanmean(data, axis=0)
    sem = stats.sem(data, axis=0, nan_policy='omit')
   
    if len(time) < len(average):
        a = len(time)
        average = average[0:a]
        sem = sem[0:a]
    elif len(average) < len(time):
        a = len(average)
        time = time[0:a]
   
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.errorbar(time, average, yerr=sem)
    plt.xlabel('time in h')
    plt.ylabel('relative organoid size')
    plt.title(title)
    if ymin != 0 or ymax != 0:
        plt.ylim((ymin, ymax))
    plt.savefig(figname)
           
def analysis(folder, pixelSize, interval, smoothing_frame, collapse_limit, file_name, removed, title, start, ymin, ymax):
    """
    analysis(folder, pixelSize, interval, smoothing_frame, collapse_limit, file_name, removed, title, start, ymin, ymax)
    
        Parameters
        ----------
            folder : string
            pixelSize : string
            interval : string
            smoothing_frame : integer
                    size of the smoothing window
            collapse_limit : float
                    gives the minimum required size reduction of an organoid for a detectable collapse event
            file_name : string
                    name of the saved excel file
            removed : string
                    string of organoid IDs which should not be further analysed
            title : string
                    title of the plot
            start : float
            ymin : float
                    ymin limit for the axis of the plot
            ymax : float
                    ymax limit for the axis of the plot
    """
    ### import data ###
    fig_name = file_name.replace('.xlsx', '.png')
    ps = float(pixelSize)**2
    time, size, circularity = read_data(folder, interval, start)
   
    ### export raw data ####
    writer = ExcelWriter(file_name, engine='xlsxwriter')
    size.to_excel(writer, sheet_name='PixelSize')
    circularity.to_excel(writer, sheet_name='Circularity')
    S = {'settings' : Series([pixelSize, interval, smoothing_frame, collapse_limit, removed], index=['pixel size', 'interval', 'smoothing frame', 'collapse limit', 'removed organoids'])}
    settings = DataFrame(S)
    settings.to_excel(writer, sheet_name='Settings')

    ### growth analysis ###
    organoids = list(size.index)
    if not removed == '':
        to_remove = removed.split('&')
        for r in to_remove:
            ir = organoids.index(int(r))
            size.drop(size.index[ir], inplace=True)
            organoids = size.index.values.tolist()
    SizeMatrix = size.values.tolist()
    create_plot(SizeMatrix, time, fig_name, title, ymin, ymax)
   
    df = DataFrame(columns = ['Label', 'InitialSize', 'FinalSize','MinimalSize', 'MaximalSize', 'CollapseEvents', 'CollapseEndEvents', 'ExpansionStart', 'ExpansionEnd', 'ExpansionSlope', 'ExpansionSlopeCoeff', 'av. exp. speed', 'max. exp. speed'])
    ident = 0
    for organoid in SizeMatrix:
        j = SizeMatrix.index(organoid)
        yVector = organoid
        start_v = 0
        for v in yVector:
            if math.isnan(v) == False:
                start_v = yVector.index(v)
                break
        y_vec = yVector[start_v:]
        last = len(y_vec)
        for v in y_vec:
            if math.isnan(v) == True:
                last = y_vec.index(v)
                break
        last_v = start_v+last
        y_vec = yVector[start_v:last_v]
        time2 = time[start_v:last_v]
        df.set_value(ident, 'Label', organoids[j])
        START = y_vec[5]
        END = y_vec[-1]
        Min = min(float(s) for s in y_vec)
        Minimum = Min*ps
        start = y_vec.index(Min)
        Max = max(float(s) for s in y_vec)
        Maximum = Max*ps
        df.set_value(ident, 'InitialSize', START*ps)
        df.set_value(ident, 'FinalSize', END*ps)
        df.set_value(ident, 'MinimalSize', Minimum)
        df.set_value(ident, 'MaximalSize', Maximum)
        normalization = y_vec[5]
        relative_size = []
        for i in y_vec:
            r_size = i/normalization
            relative_size.append(r_size)
        smoothed = moving_average(relative_size, smoothing_frame)
        collapse, collapse_end = find_collapse(time2, relative_size, collapse_limit, True)
        if len(collapse) > 0 :
            ce = []
            for c in collapse:
                if c > start:
                    cv = time2[c]
                    ce.append(cv)
        else:
            ce = '-'
        if ce == []:
            ce = '-'
        df.set_value(ident, 'CollapseEvents', ce)
       
        if len(collapse_end) > 0 :
            ce = []
            for c in collapse_end:
                if c > start:
                    cv = time2[c]
                    ce.append(cv)
        else:
            ce = '-'
        if ce == []:
            ce = '-'
        df.set_value(ident, 'CollapseEndEvents', ce)
        
        phases_up = phase_characterization(time2, smoothed, collapse, collapse_end)
       
        if phases_up == []:
            av = '-'
            mx = '-'
            df.set_value(ident, 'av. exp. speed', av)
            df.set_value(ident, 'max. exp. speed', mx)
        else:
            array = np.array(phases_up)
            av = np.nanmean(array, axis=0)
            mx = np.amax(array, axis=0)
            df.set_value(ident, 'av. exp. speed', av[2])
            df.set_value(ident, 'max. exp. speed', mx[2])
 
        if len(phases_up) > 0:
            start_t = []
            end_t = []
            slope_t = []
            rval_t = []
            for i in range(0, len(phases_up)):
                phase = phases_up[i]
                start_t.append(phase[0]*float(interval))
                end_t.append(phase[1]*float(interval))
                slope_t.append(phase[2])
                rval_t.append(phase[3])
            df.set_value(ident, 'ExpansionStart', start_t)
            df.set_value(ident, 'ExpansionEnd', end_t)
            df.set_value(ident, 'ExpansionSlope', slope_t)
            df.set_value(ident, 'ExpansionSlopeCoeff', rval_t)
        else:
            df.set_value(ident, 'ExpansionStart', '-')
            df.set_value(ident, 'ExpansionEnd', '-')
            df.set_value(ident, 'ExpansionSlope', '-')
            df.set_value(ident, 'ExpansionSlopeCoeff', '-')
        ident = ident + 1
    df.to_excel(writer, sheet_name='Analysis')
    writer.save()


