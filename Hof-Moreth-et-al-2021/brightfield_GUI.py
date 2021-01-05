from PyQt5.QtWidgets import QApplication, QDialog, QWidget, QPushButton, QMainWindow, QLineEdit, QLabel, QHBoxLayout, QVBoxLayout, QFileDialog, QComboBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from PyQt5 import QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import brightfield_functions as functions
import numpy as np
import sys, os
import math
import matplotlib.pyplot as plt
from scipy import stats

sampleData = r'R:\groups\stelzerall\2019_OrgaLivePaper_raw-data\Github\Brightfield_pipeline\sampleData'

fiji = r'R:\users\lhof\Students\MA_JuliaTarnick\Fiji-1.51n\ImageJ-win64.exe'
stitching_macro = r'R:\groups\stelzerall\2019_OrgaLivePaper_raw-data\Github\Brightfield_pipeline\stitching.ijm'
segmentation_macro = r'R:\groups\stelzerall\2019_OrgaLivePaper_raw-data\Github\Brightfield_pipeline\AutomaticOrganoidSegmentation.ijm'
omero_upload_macro = r'R:\groups\stelzerall\2019_OrgaLivePaper_raw-data\Github\Brightfield_pipeline\omero_upload.py'
segmentation_only_macro = r'R:\groups\stelzerall\2019_OrgaLivePaper_raw-data\Github\Brightfield_pipeline\segmentation2.ijm'
label_edition_macro = r'R:\groups\stelzerall\2019_OrgaLivePaper_raw-data\Github\Brightfield_pipeline\editLabels.ijm'

class AppForm(QMainWindow):
    """
    AppForm(QMainWindow)
        Graphical User Interface (GUI) to analyse growth dynamics of organoids
    
        The GUI allows to load Brightfield experimental data and uses the 
        functions and analysis tools implemented in brightfield_functions.py
        in order to quantify parameters from experimental data i.e. growth dynamics
    """
    
    def __init__(self, parent=None):
        """
        __init__(self, parent=None)
            constructor for the GUI determining the form and initializes values 
            
            Values
            ------
                pixel size : 1.29
                start time : 0
                interval in h : 0.5
                smoothing frame : 5
                collapse limit in % : 10
        """
        
        QMainWindow.__init__(self, parent)
        self.setWindowTitle('Organoid growth analysis')
        self.setWindowIcon(QIcon('icon.png'))
        self.create_main_frame()
        self.smoothing.setText('5')
        self.directory.setText(sampleData)
        self.collapse_limit.setText('10')
        self.pixel_size.setText('1.29')
        self.interval.setText('0.5')
        self.removed.setText('')
        self.title.setText('title')
        self.on_draw()


    def save_parameters(self):
        """
        save_parameters(self)
            saves current parameters to a .txt file
            
            the function is found in the menu bar
                -> paramter
        """
        
        interval = self.interval.text()
        pixelsize = self.pixel_size.text()
        smoothing = self.smoothing.text()
        c_limit = self.collapse_limit.text()
        file_choices = "TXT (*.txt)|*.txt"
        output = QFileDialog.getSaveFileName(self, 'Save file', '', file_choices)
        file = open(output[0], 'w')
        file.write(interval+'_interval\n')
        file.write(pixelsize+'_pixel size\n')
        file.write(smoothing+'_smoothing frame\n')
        file.write(c_limit+'_collapse limit')
        file.close()
        
    def load_parameters(self):
        """
        load_parameters(self)
            loads parameters from a .txt file
            
            the function is found in the menu bar
                -> paramter
        """       
    
        file_choices = "TXT (*.txt)|*.txt"
        input_file = QFileDialog.getOpenFileName(self, 'open file', '', file_choices)
        with open(input_file[0]) as f:
            parameters = f.readlines()
        interv = parameters[0].split('_')
        self.interval.setText(interv[0])
        ps = parameters[1].split('_')
        self.pixel_size.setText(ps[0])
        smo = parameters[2].split('_')
        self.smoothing.setText(smo[0])
        ce = parameters[3].split('_')
        self.collapse_limit.setText(ce[0])
        self.on_draw()


    def on_draw(self):
        """
        on_draw(self)
            plots the current organoid data
            
            the function is called when
              -> new data is loaded (Select Directory)
              -> the current organoid is switched
              -> the parameter "collapse limit in %" is changed
        """

        self.axes.cla()
        folder = self.directory.text()
        removed = self.removed.text()
        interval = self.interval.text()
        start = float(self.start.text())
        time, size, circularity = functions.read_data(folder, interval, start)
        organoids = size.index.values.tolist()
        print()
        if not removed == '':
            to_remove = removed.split('&')
            for r in to_remove:
                ir = organoids.index(int(r))
                size.drop(size.index[ir], inplace=True)
                organoids = size.index.values.tolist()
        size_matrix = size.values.tolist()
        self.sld.setMaximum(len(size_matrix))
        org = self.sld.value()-1
        y_vec = size_matrix[org]
        start_v = 0
        for v in y_vec:
            if math.isnan(v) == False:
                start_v = y_vec.index(v)
                break
        y_vec2 = y_vec[start_v:]
        last = len(y_vec2)
        for v in y_vec2:
            if math.isnan(v) == True:
                last = y_vec2.index(v)
                break
        last_v = start_v+last
        y_vec = y_vec[start_v:last_v]
        time2 = time[start_v:last_v]
        Min = min(float(s) for s in y_vec)
        start = y_vec.index(Min)
        
        # normalize data
        normalization = y_vec[5]
        relative_size = []
        for i in y_vec:
            r_size = i / normalization
            relative_size.append(r_size)
        frame = int(self.smoothing.text())
        
        # smoothe data
        smoothed = functions.moving_average(relative_size, frame)
        
        # find collapse events
        c_limit = float(self.collapse_limit.text())
        collapse, end_collapse = functions.find_collapse(time2, relative_size, c_limit, True)
        
        # plot collapse events
        if len(collapse) > 0:
            ce = []
            for c in collapse:
                if c > start:
                    cv = time2[c]
                    ce.append(cv)
                    a = ce.index(cv)
                    
                    self.axes.plot(time2[c], relative_size[c], 'or', label='collapse' if len(ce) == 1 else '')
            
        if len(end_collapse) > 0:
            cee = []
            for c in end_collapse:
                if c > start:
                    cv2 = time2[c]
                    cee.append(cv2)
                    
                    self.axes.plot(time2[c], relative_size[c], 'ob', label='end collapse' if len(cee) == 1 else '')
                    
        # characterize growth and deflation phases and plot them
        phases = functions.phase_characterization(time2, relative_size, collapse, end_collapse)
        for p in phases:
            a = p[0]
            b = p[1]
            x = time2[a:b]
            fit = np.polyfit(time2[a:b], relative_size[a:b], 1)
            fit_fn = np.poly1d(fit)
            self.axes.plot(x, fit_fn(x), 'm', label='expansion phase' if phases.index(p) == 0 else '')
        self.axes.plot(time2, relative_size, '--k', label='normalized growth curve')
        self.axes.plot(time2, smoothed, '--b', label='smoothed growth curve')
        self.axes.legend(loc='upper center', bbox_to_anchor=(0.5, -0.07), ncol=4, fontsize='small')
        self.axes.set_title('organoid: ' + str(organoids[org]))
        self.canvas.draw()


    def start_analysis(self):
        """
        start_analysis(self)
            analyses the loaded data under the given parametercombinations
            saves the analyzed data to a .xlsx file
        """
        
        file_choices = "XLSX (*.xlsx)|*.xlsx"
        output = QFileDialog.getSaveFileName(self, 'Save file', '', file_choices)
        start = float(self.start.text())
        path = output[0]
        input_dir = self.directory.text()
        pixel_size = self.pixel_size.text()
        interval = self.interval.text()
        smoothing = self.smoothing.text()
        c_limit = self.collapse_limit.text()
        to_remove = self.removed.text()
        title = self.title.text()
        if self.cb.isChecked():
            ymin = float(self.ymin.text())
            ymax = float(self.ymax.text())
        else:
            ymin = 0
            ymax = 0
        functions.analysis(input_dir, pixel_size, interval, int(smoothing), float(c_limit), path, to_remove, title, start, ymin, ymax)
  
    
    def remove_organoid(self):
        """
        remove_organoid(self)
            allows to remove the currently shown organoid due to 
            visual inspection
            
            the function is called via a button (Remove organoid from analyis)
        """
        org = self.sld.value()-1
        folder = self.directory.text()
        interval = self.interval.text()
        removed = self.removed.text()
        start = float(self.start.text())
        time, size, circularity = functions.read_data(folder, interval, start)
        organoids = size.index.values.tolist()
        to_remove = organoids[org]
        if removed == '':
            self.removed.setText(str(to_remove))
        else:
            string = removed+'&'+str(to_remove)
            self.removed.setText(string)
        self.on_draw()
 
    
    def open_folder(self):
        """
        open_folder(self)
            calls the explorer to navigate to a certain folder
            
            the function is called via a button (Select Directory)
        """
        path = QFileDialog.getExistingDirectory(self, "Select Directory")
        self.directory.setText(path)
        self.removed.setText('')
        self.on_draw()
    
    
    def keyPressEvent(self, qKeyEvent):
        """
        keyPressEvent(self, qKeyEvent)
            allows to change the displayed organoid
            
            the function is called via a scroll bar
        """
        if qKeyEvent.key() == Qt.Key_Return: 
            self.on_draw()

    
    def stitching(self):
        """
        stitching(self)
            calls a Fiji Macro which analyzes the originial image data and
            combines smaller subimages to the final images
        """
        dialog = Dialog()
        dialog.exec_()
        dialog.show()
        
        
    def segment(self):
        """
        stitching(self)
            calls a Fiji Macro which segments the originial image data
        """
        dialog = Dialog2()
        dialog.exec_()
        dialog.show()
    
    def plot_preview(self):
        """
        plot_preview(self)
            saves the displayed graphs to .png files
        """
        path = QFileDialog.getExistingDirectory(self, "Select Directory")
        folder = self.directory.text()
        removed = self.removed.text()
        interval = self.interval.text()
        start = float(self.start.text())
        time, size, circularity = functions.read_data(folder, interval, start)
        organoids = size.index.values.tolist()
        if not removed == '':
            to_remove = removed.split('&')
            for r in to_remove:
                ir = organoids.index(int(r))
                size.drop(size.index[ir], inplace=True)
        size_matrix = size.values.tolist()
        for organoid in size_matrix:
            plt.cla()
            o = size_matrix.index(organoid)
            figname = path + '\\organoid_'+str(organoids[o])+'.png'
            striped = [x for x in organoid if str(x) != 'nan']
            if len(striped ) < len(organoid)-3:
                continue
            else:
                yVector = organoid 
            start_v = 0
            for v in yVector:
                if math.isnan(v) == False:
                    start_v = yVector.index(v)
                    break
            y_vec2 = yVector[start_v:]
            last = len(y_vec2)
            for v in y_vec2:
                if math.isnan(v) == True:
                    last = y_vec2.index(v)
                    break
            last_v = start_v+last
            yVector = yVector[start_v:last_v]
            time2 = time[start_v:last_v]
            Min = min(float(s) for s in yVector)
            start = yVector.index(Min)
            normalization = yVector[5]
            relative_size = []
            for i in yVector:
                r_size = i / normalization
                relative_size.append(r_size)
            frame = int(self.smoothing.text())
            smoothed = functions.moving_average(relative_size, frame)
            c_limit = float(self.collapse_limit.text())
            collapse, collapse_end = functions.find_collapse(time2, relative_size, c_limit, True)
            if len(collapse) > 0:
                ce = []
                for c in collapse:
                    if c > start:
                        cv = time2[c]
                        ce.append(cv)
                        a = ce.index(cv)
                        self.axes.plot(time2[c], relative_size[c], 'or', label='collapse' if len(ce) == 1 else '')
            
            phases = functions.phase_characterization(time2, relative_size, collapse, collapse_end)
            for p in phases:
                a = p[0]
                b = p[1]
                x = time2[a:b]
                fit = np.polyfit(time2[a:b], relative_size[a:b], 1)
                fit_fn = np.poly1d(fit)
                plt.plot(x, fit_fn(x), 'm')
            plt.plot(time2, relative_size, ':k')
            plt.plot(time2, smoothed, '--b')
            plt.legend()
            plt.ylabel('relative size')
            plt.xlabel('time [h]')
            plt.title('organoid '+str(organoids[o]))
            plt.savefig(figname)
                
    def batch_analysis(self):
        """
        batch_analysis(self)
            allows the processing of a batch of data
        """
        file_choices = "TXT (*.txt)|*.txt"
        input_file = QFileDialog.getOpenFileName(self, 'open input file', '', file_choices)
        outfolder = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        beginn = float(self.start.text())
        pixel_size = self.pixel_size.text()
        interval = self.interval.text()
        smoothing = self.smoothing.text()
        c_limit = self.collapse_limit.text()
        to_remove = self.removed.text()
        fig = plt.figure(figsize=(10,6))
        if self.cb.isChecked():
            ymin = float(self.ymin.text())
            ymax = float(self.ymax.text())
        else:
            ymin = 0
            ymax = 0
        with open(input_file[0]) as f:
            lines = f.readlines()
            for l in lines:
                text = l.split('|')
                condition = text[0]
                folder = text[1].rstrip()
                output = outfolder+'//'+condition+'.xlsx'
                functions.analysis(folder, pixel_size, interval, int(smoothing), int(c_limit), output, to_remove, condition, beginn, ymin, ymax)
                time, size, circularity = functions.read_data(folder, interval, beginn)
                SizeMatrix = size.values.tolist()
                striped = []
                for j in range(0, len(SizeMatrix)):
                    short = [x for x in SizeMatrix[j] if str(x) != 'nan']
                    vec = SizeMatrix[j]
                    r_vec = [x / short[5] for x in vec]
                    start = 0
                    for i in range(0, len(r_vec)+1):
                        if math.isnan(vec [i]) == False:
                            start = i
                            vec2 = r_vec[start:]
                            break
                    while len(vec2) < len(SizeMatrix[0]):
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
                c = np.random.rand(3)
                ax = fig.add_subplot(111)
                ax.set_position([0.1,0.1,0.7,0.8])
                ax.errorbar(time, average, yerr=sem, color=c, label=condition)
                plt.xlabel('time in h')
                plt.ylabel('relative organoid size')
            ax.legend(loc = 'center left', bbox_to_anchor=(1, 0.8))
            figurename = outfolder+'//summary.png'
            fig.savefig(figurename)
            plt.show()
    
    
    def segmentation_only (self):
        """
        segmentation_only(self)
            calls a FIJI Macro to segment the current data
        """
        dialog = Dialog2b()
        dialog.exec_()
        dialog.show()
        
    def label_edition (self):
        
        file_choices = "TIF (*.tif)|*.tif"
        path = QFileDialog.getOpenFileName(self, 'select image', '', file_choices)
        image = str(path[0])
        os.system(fiji+' -macro '+label_edition_macro+' ' + image)
        
    
    def batch_stitching(self):
        """
        batch_stitching(self)
            allows the stiching of a batch of data
        """
        dialog = Dialog1b()
        dialog.exec_()
        dialog.show()
        
    def create_main_frame(self):
        """
        create main_frame(self)
            creates the main frame GUI with the given input standard data
        """
        self.main_frame = QWidget()
        self.dpi = 100
        self.fig = Figure((5.0, 4.0), dpi=self.dpi)
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self.main_frame)
        self.axes = self.fig.add_subplot(111)
        
        l1 = QLabel('start time')
        l2 = QLabel('dataset')
        l3 = QLabel('smoothing frame')
        l4 = QLabel('collapse limit in %')
        l5 = QLabel('pixel size')
        l6 = QLabel('interval in h')
        l7 = QLabel('removed organoids')
        
        self.start = QLineEdit()
        self.start.setText('0')
        self.start.setMaximumWidth(50)
        self.smoothing = QLineEdit()
        self.smoothing.setMaximumWidth(50)
        self.directory = QLineEdit()
        self.collapse_limit = QLineEdit()
        self.collapse_limit.setMaximumWidth(50)
        self.pixel_size = QLineEdit()
        self.pixel_size.setMaximumWidth(50)
        self.interval = QLineEdit()
        self.interval.setMaximumWidth(50)
        self.removed = QLineEdit()
        
        self.title = QLineEdit()
        self.title.setMinimumWidth(300)
        self.ymin = QLineEdit()
        self.ymin.setMaximumWidth(50)
        self.ymax = QLineEdit()
        self.ymax.setMaximumWidth(50)
        self.cb = QtWidgets.QCheckBox('fixed y axis range from')
        l8 = QLabel('to')
    
        self.sld = QtWidgets.QScrollBar(Qt.Horizontal)
        self.sld.setMinimum(1)
        self.sld.valueChanged.connect(self.on_draw)

        analysis_button = QPushButton("&Start Analysis")
        analysis_button.clicked.connect(self.start_analysis)
        remove_button = QPushButton("&Remove organoid from analysis")
        remove_button.clicked.connect(self.remove_organoid)
        input_button = QPushButton("&Select Directory")
        input_button.clicked.connect(self.open_folder)
       
        
        menubar = QtWidgets.QMenuBar()
        stitchAction = QtWidgets.QAction('&stitch images', self)
        stitchAction.triggered.connect(self.stitching)
        segmentAction = QtWidgets.QAction('&segment and edit', self)
        segmentAction.triggered.connect(self.segment)
        segment2 = QtWidgets.QAction('&segment and save', self)
        segment2.triggered.connect(self.segmentation_only)
        edit = QtWidgets.QAction('&edit labels', self)
        edit.triggered.connect(self.label_edition)
        imageMenu = menubar.addMenu("&image processing")
        imageMenu.addAction(stitchAction)
        imageMenu.addAction(segmentAction)
        imageMenu.addAction(segment2)
        imageMenu.addAction(edit)
        
        saveParameter = QtWidgets.QAction('&save parameter', self)
        saveParameter.triggered.connect(self.save_parameters)
        loadParameter = QtWidgets.QAction('&load parameter', self)
        loadParameter.triggered.connect(self.load_parameters)
        parameterMenu = menubar.addMenu("&parameter")
        parameterMenu.addAction(saveParameter)
        parameterMenu.addAction(loadParameter)
        
        batchMenu = menubar.addMenu("&batch processing")
        batchAnalysis = QtWidgets.QAction("&batch analysis", self)
        batchAnalysis.triggered.connect(self.batch_analysis)
        batchStitching = QtWidgets.QAction("&batch stitching", self)
        batchStitching.triggered.connect(self.batch_stitching)
        batchMenu.addAction(batchAnalysis)
        batchMenu.addAction(batchStitching)
        
        plotMenu = menubar.addMenu("&plot")
        preview = QtWidgets.QAction("&save preview plots", self)
        preview.triggered.connect(self.plot_preview)
        plotMenu.addAction(preview)
        
        hbox = QHBoxLayout()
        for w in [input_button, l2, self.sld]:
            hbox.addWidget(w)
        hbox2 = QHBoxLayout()
        for y in [remove_button, l7, self.removed, analysis_button]:
            hbox2.addWidget(y)
        hbox3 = QHBoxLayout()
        for w in [l5, self.pixel_size,l1, self.start, l6, self.interval, l3, self.smoothing, l4, self.collapse_limit]:
            hbox3.addWidget(w)
        
        hbox6 = QHBoxLayout()
        for w in [self.title, self.cb, self.ymin, l8, self.ymax]:
            hbox6.addWidget(w)
        vbox = QVBoxLayout()
        vbox.addWidget(menubar)
       
        vbox.addLayout(hbox)
        vbox.addLayout(hbox6)
        vbox.addWidget(self.canvas)
        vbox.addLayout(hbox3)
        vbox.addLayout(hbox2)
        
        self.main_frame.setLayout(vbox)
        self.setCentralWidget(self.main_frame)
        
        
class Dialog(QDialog): 
    
    def __init__(self):
        
        QDialog.__init__(self) 
        Dialog.setWindowTitle(self, "tile stitching")
        btn_browse = QPushButton("&select directory")
        btn_browse.clicked.connect(self.get_directory)
        self.folder = QLineEdit()
        btn_start = QPushButton("&start")
        btn_start.clicked.connect(self.start_stitching)
        l1 = QLabel('grid size x')
        self.grid_x = QLineEdit()
        l2 = QLabel('grid size y')
        self.grid_y = QLineEdit()    
        l3 = QLabel('overlap')
        self.overlap = QLineEdit()      
        l4 = QLabel('number of z planes')
        self.z_planes = QLineEdit()      
        l5 = QLabel('number of time points')
        self.time_points = QLineEdit()       
        l6 = QLabel('image prefix')
        self.prefix = QLineEdit() 
        l7 = QLabel('image suffix')
        self.suffix = QLineEdit()
        self.suffix.setText('_ORG.tif')
        vbox = QVBoxLayout()
        l8 = QLabel('DatasetID')
        self.dID = QLineEdit()
        self.cb = QtWidgets.QCheckBox('upload to omero')
        hbox = QHBoxLayout()
        for w in [self.cb, l8, self.dID]:
            hbox.addWidget(w)
        for w in [btn_browse, l6, self.prefix, l7, self.suffix, l1, self.grid_x, l2, self.grid_y, l3, self.overlap, l4, self.z_planes, l5, self.time_points, btn_start]:
            vbox.addWidget(w)
        vbox.addLayout(hbox)
        self.setLayout(vbox)
        
        
    def get_directory(self):
        
          path = QFileDialog.getExistingDirectory(self, "Select Directory")
          self.folder.setText(path)
       
        
    def start_stitching(self):
        
        file_choices = "TIF (*.tif)|*.tif"
        output = QFileDialog.getSaveFileName(self, 'Save file', '', file_choices)
        outfile = output[0]
        directory = self.folder.text()
        prefix = self.prefix.text()
        zplanes = self.z_planes.text()
        overlap = self.overlap.text()
        timepoints = self.time_points.text()
        gridx = self.grid_x.text()
        gridy = self.grid_y.text()
        suffix = self.suffix.text()
        arguments = directory+'#'+prefix+'#'+zplanes+'#'+overlap+'#'+timepoints+'#'+gridx+'#'+gridy+'#'+suffix+'#'+outfile
        print(arguments)
        os.system(fiji+' -macro '+ stitching_macro + ' ' + arguments)
        did = self.dID.text()
        if self.cb.isChecked():
            os.system(fiji+' -macro '+ omero_upload_macro + ' '+outfile+'#'+did)
        self.close()


class Dialog1b(QDialog): 
    """
    Dialog1b(QDialog)
        asks fr metadata for the stitching process
        offers to upload results to omero under a given ID
    """
    def __init__(self):
        
        QDialog.__init__(self) 
        Dialog.setWindowTitle(self, "tile stitching")
        btn_start = QPushButton("&start")
        btn_start.clicked.connect(self.start_stitching)
        l1 = QLabel('grid size x')
        self.grid_x = QLineEdit()
        l2 = QLabel('grid size y')
        self.grid_y = QLineEdit()    
        l3 = QLabel('overlap')
        self.overlap = QLineEdit()      
        l4 = QLabel('number of z planes')
        self.z_planes = QLineEdit()            
        l7 = QLabel('image suffix')
        self.suffix = QLineEdit()
        self.suffix.setText('_ORG.tif')
        vbox = QVBoxLayout()
        l8 = QLabel('DatasetID')
        self.dID = QLineEdit()
        self.cb = QtWidgets.QCheckBox('upload to omero')
        hbox = QHBoxLayout()
        for w in [self.cb, l8, self.dID]:
            hbox.addWidget(w)
        for w in [l7, self.suffix, l1, self.grid_x, l2, self.grid_y, l3, self.overlap, l4, self.z_planes, btn_start]:
            vbox.addWidget(w)
        vbox.addLayout(hbox)
        self.setLayout(vbox)
        
    def start_stitching(self):
        
        file_choices = "TXT (*.txt)|*.txt"
        input_file = QFileDialog.getOpenFileName(self, 'open input file', '', file_choices)
        with open(input_file[0]) as f:
            lines = f.readlines()
            for l in lines:
                text = l.split('|')
                prefix = text[0]
                directory = text[1]
                timepoints = text[2].rstrip()
                outfile = directory+'//'+prefix+'_stitched.tif'
                zplanes = self.z_planes.text()
                overlap = self.overlap.text()
                gridx = self.grid_x.text()
                gridy = self.grid_y.text()
                suffix = self.suffix.text()
                arguments = directory+'#'+prefix+'#'+zplanes+'#'+overlap+'#'+timepoints+'#'+gridx+'#'+gridy+'#'+suffix+'#'+outfile
                print(arguments)
                os.system(fiji+' -macro '+ stitching_macro + ' ' + arguments)
                did = self.dID.text()
                if self.cb.isChecked():
                    os.system(fiji+' -macro '+ omero_upload_macro + ' '+outfile+'#'+did)
                self.close()


class Dialog2(QDialog):
    """
    Dialog2(QDialog)
        preprocessing for the segmentation
        the Dialogbox asks for a directory, which filter to apply
        offers to save preliminary segmentation results
        offers to upload data to omero under a given ID
    """
    def __init__(self):
        
        QDialog.__init__(self)
        Dialog2.setWindowTitle(self, "segmentation")
        btn_input = QPushButton("&select image")
        btn_input.clicked.connect(self.get_image)
        self.input_image = QLineEdit() 
        l9 = QLabel('select filter')
        self.filterBox = QComboBox()
        self.filterBox.addItem("median")
        self.filterBox.addItem("sigma")
        self.filterBox.addItem("bilateral")
        btn_segmentation = QPushButton("&start")
        btn_segmentation.clicked.connect(self.start_segmentation)
        self.cb2 = QtWidgets.QCheckBox('save intermediate')
        l8 = QLabel('DatasetID')
        self.dID = QLineEdit()
        self.cb = QtWidgets.QCheckBox('upload to omero')
        hbox = QHBoxLayout()
        for w in [self.cb, l8, self.dID]:
            hbox.addWidget(w)
        vbox = QVBoxLayout()
        for w in [btn_input, l9, self.filterBox, self.cb2, btn_segmentation]:
            vbox.addWidget(w)
        vbox.addLayout(hbox)
        self.setLayout(vbox)


    def get_image(self):

        file_choices = "TIF (*.tif)|*.tif"
        path = QFileDialog.getOpenFileName(self, 'select image', '', file_choices)
        self.input_image.setText(str(path[0]))
 
       
    def start_segmentation(self):

        filterChoice = self.filterBox.currentText()
        image = self.input_image.text()
        if self.cb2.isChecked():
            save = 'yes'
        else:
            save = 'no'
        arg = image+'#'+filterChoice+'#'+save
        os.system(fiji+' -macro '+segmentation_macro+' ' + arg)
        self.close()
        outfile = image + '_segmented.tif'
        did = self.dID.text()
        if self.cb.isChecked():
            os.system(fiji+' -macro '+ omero_upload_macro + ' '+outfile+'#'+did)
        if self.cb.isChecked():
            os.system(fiji+' -macro '+ omero_upload_macro + ' '+image+'#'+did)
        self.close()
    
    
class Dialog2b(QDialog):
    """
    Dialog2b(QDialog)
        preprocessing for the segmentation
        the Dialogbox asks for a directory, which filter to apply
        offers to upload data to omero under a given ID
    """
    def __init__(self):
        
        QDialog.__init__(self)
        Dialog2.setWindowTitle(self, "segmentation")
        btn_input = QPushButton("&select image")
        btn_input.clicked.connect(self.get_image)
        self.input_image = QLineEdit() 
        l9 = QLabel('select filter')
        self.filterBox = QComboBox()
        self.filterBox.addItem("median")
        self.filterBox.addItem("sigma")
        self.filterBox.addItem("bilateral")
        btn_segmentation = QPushButton("&start")
        btn_segmentation.clicked.connect(self.start_segmentation)
        l8 = QLabel('DatasetID')
        self.dID = QLineEdit()
        self.cb = QtWidgets.QCheckBox('upload to omero')
        hbox = QHBoxLayout()
        for w in [self.cb, l8, self.dID]:
            hbox.addWidget(w)
        vbox = QVBoxLayout()
        for w in [btn_input, l9, self.filterBox, btn_segmentation]:
            vbox.addWidget(w)
        vbox.addLayout(hbox)
        self.setLayout(vbox)


    def get_image(self):

        file_choices = "TIF (*.tif)|*.tif"
        path = QFileDialog.getOpenFileName(self, 'select image', '', file_choices)
        self.input_image.setText(str(path[0]))
 
       
    def start_segmentation(self):

        filter = self.filterBox.currentText()
        image = self.input_image.text()
        arg = image+'#'+filter
        os.system(fiji+' -macro '+segmentation_only_macro+' ' + arg)
        self.close()
        outfile = image + '_segmented.tif'
        did = self.dID.text()
        if self.cb.isChecked():
            os.system(fiji+' -macro '+ omero_upload_macro + ' '+outfile+'#'+did)
        if self.cb.isChecked():
            os.system(fiji+' -macro '+ omero_upload_macro + ' '+image+'#'+did)
        self.close()
     
    
def main():
    
    app = QApplication(sys.argv)
    form = AppForm()
    form.show()
    app.exec_()

if __name__ == "__main__":
    main()
