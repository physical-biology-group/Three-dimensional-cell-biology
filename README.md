# Three-dimensional cell biology


### Supplementary material of Hof, Moreth et al. 2021

##### Hof, L*; Moreth, T*; Koch, M; Liebisch, T; Kurtz, M; Tarnick, J; Lissek, S; Verstegen, M; van der Laan, L; Huch, M; Matthäus, F; Stelzer, EHK; Pampaloni, F; (2021) "Long-term live imaging and multiscale analysis identify heterogeneity and core principles of epithelial organoid morphogenesis"

The bright field pipeline was implemented in Python 3.6

All code is provided as .py and .ijm (ImageJ).

"brightfield_GUI.py" contains the graphical user interface (GUI) of the pipeline.

"brightfield_functions.py" contains the functions of the pipeline.

The folder "Brightfield_pipeline" contains "sampleData" needed to start the GUI as well as ImageJ-Macros applied in "brightfield_functions."
The folder "Brightfield_pipeline" has to be saved and lines 14 - 21 of "brightfield_GUI" have to be adjusted accordingly.

In line 16, Fiji-1.51n.exe has to be called inlcuding the MorphoLibJ-1.2.2.-Plugin (Legland, D.; Arganda-Carreras, I. & Andrey, P. (2016), "MorphoLibJ: integrated library and plugins for mathematical morphology with ImageJ", Bioinformatics (Oxford Univ Press) 32(22): 3532-3534, PMID 27412086, doi:10.1093/bioinformatics/btw413)

All further information regarding the analysis is contained in the scripts.

For questions and comments please contact Francesco Pampaloni (fpampalo@bio.uni-frankfurt.de).
