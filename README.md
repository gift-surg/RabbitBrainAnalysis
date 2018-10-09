# Rabbit Brain Analysis

The pipeline to manipulate and analyse MRI data from the "Encephalopaty of prematurity" project, in collaboration with KU Leuven.


<p align="center"> 
<img src="https://github.com/gift-surg/RabbitBrainAnalysis/blob/master/notes/hat_logo.jpg" width="500">
</p>


#### Features:

+ This is a data-specific code developed for the encephalophaty of prematurity project. 
+ Input of the pipeline is the subject scanned in the native Bruker format. 
+ Output of the pipeline is the subject oriented and segmented provided with subject-wise and comparative data analysis.  
+ **WARNING** the code is developed to be `research code` (read: 80% is an uncommented work in progress, not packaged to be a product. [See research code definition](https://academia.stackexchange.com/questions/21276/best-practice-models-for-research-code))
+ The code is developed in collaboration with University College London UCL, King's College London (KCL) and Katholische Universitat Leuven (KUL).
+ Pipeline schema can be found under notes folder.
+ Based on libraries in `requriements.txt` (there are non pip-installable dependencies: follow installation instructions directly from the README library repository) other than niftyReg niftySeg and FSL
+ Package `main_pipeline` has the strucure of the pipeline as in the schematic of the documentation.
+ Each module of the pipeline can run independently (for debugging and single step analysis) or as part of
the whole pipeline, if called by the `main`.


#### How to use - basic run:

+ Connect to the dataset (NAS `Emporioum` if at KCL) and the rabbit dataset folder structure (can be used also on the cluster after updating dataset).
+ Run `A0_main/subject_parameters_creator.py` to have the latest parameters file (created parameters file connects the subject name 
with its chart, containing all the information related to the subject - e.g. study, category, orientation...)
+ Select the parts that you want to run and the subject you want to apply the pipeline in the `A0_main/main_executer.py`
+ Run `main_executer.py`.
+ Raise an issue if something goes wrong.


#### How to use - add new scans to the database:

+ Update the log of the received files in the root of rabbit analysis in Emporium.
+ Follow existing folder structure (see under notes) and store the .zip in the appropriate place.
+ Rename the zip to only the filename (following the exising structure).

#### How to use - elaborate the newly acquired subject:

+ add the chart of the new subject in the file `A0_main/subject_parameters_creator.py` with default values.
+ start the A0 phase of the pipeline.
+ see the converted subject and update the parameters under `A0_main/subject_parameters_creator.py` according to 
visual intuition.
+ re run `A0_main/subject_parameters_creator.py` to update parameters.
+ run the whole pipeline `main_executer.py` for the selected subject.

#### TODO

+ Main work in progress is under `danny_approval`. [Danny](https://github.com/SebastianoF/DummyForMRI) (see crash testing) is a dummy dataset created with the github repository
DummyForMRI. Under danny approval we intend to develop some automatic testing to automatically perform the 
 pipeline on the Danny, and check possible issues.
 

#### Memorandum - git usage:

To push latest commits on the GIFTSurg repo use 
```bash
#git remote add origin_gs https://github.com/gift-surg/RabbitBrainAnalysis.git
git push origin_gs master
```

To push latest commits on the CMIClab platform (until 15-sept 2018) use
```
git push origin_gs master
```

To check the remote origin in your local repository type:
```
git remote -v
```

## Acknowledgements
+ This repository is developed within the [GIFT-surg research project](http://www.gift-surg.ac.uk).
+ This work was supported by Wellcome / Engineering and Physical Sciences Research Council (EPSRC) [WT101957; NS/A000027/1; 203145Z/16/Z].