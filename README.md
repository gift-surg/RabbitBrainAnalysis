# Rabbit Brain Analysis

The pipeline to manipulate MRI data from the "Encephalopaty of prematurity" project, in collaboration with KU Leuven.


#### Features:

+ Private repository: may be too data-specific to be publicly useful.
+ Pipeline schema can be found under notes folder.
+ Based on libraries in requriements.txt other than niftyReg niftySeg and FSL
+ Package `main_pipeline` has the strucure of the pipeline as in the schematic of the documentation.
+ Each module of the pipeline can run independently (for debugging and single step analysis) or as part of
the whole pipeline, if called by the `main`.
+ Improvements are constant, so expect some half baked parts and many work in progress.


#### How to use - basic run:

+ connect to Emporioum and the rabbit dataset folder structure (can be used also on the cluster after updating dataset).
+ run `A0_main/subject_parameters_creator.py` to have the latest parameters file (created parameters file connects the subject name 
with its chart, containing all the information related to the subject - e.g. study, category, orientation...)
+ select the parts that you want to run and the subject you want to apply the pipeline in the `A0_main/main_executer.py`
+ run `main_executer.py`


#### How to use - add new subject to the database:

+ update the log of the received files in the root of rabbit analysis in Emporium.
+ follow existing folder structure (see under notes) and store the .zip in the appropriate place.
+ rename the zip to only the filename (following the exising structure).

#### How to use - elaborate the newly acquired subject:

+ add the chart of the new subject in the file `A0_main/subject_parameters_creator.py` with default values.
+ start the A0 phase of the pipeline.
+ see the converted subject and update the parameters under `A0_main/subject_parameters_creator.py` according to 
visual intuition.
+ re run `A0_main/subject_parameters_creator.py` to update parameters.
+ run the whole pipeline `main_executer.py` for the selected subject.

#### TODO

Main work in progress is under `danny_approval`. Danny is a dummy dataset created with the github repository
DummyForMRI. All the possible variant of the pipeline should be applied to the Danny, to quickly test the 
pipeline without using the rabbit data, that are time-consuming. 

See monkey testing and danny crash test for further infos.


#### Memorandum:

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
