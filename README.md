# CSE6242

## DESCRIPTION

Our project utilizes tracking data from the NFL to evaluate Quarterback decision-making on pass plays. The data is publicly available at https://www.kaggle.com/c/nfl-big-data-bowl-2021, replication notebooks need to be run on Kaggle in some instances. Our package parses over 18 million frames from the tracking data, which records information every tenth of a second on every play. The data is from the 2018 season only.

The following notebooks filter the data into a usable form, calculate our innovative metrics, then fits a few logisitc regression models and trains a Random Forest. Our process allows us to glean insights on Quarterback decision making, and which Quarterbacks throw to the most open receivers.

## INSTALLATION

findPlayersWithTargets.ipynb - Run this code on Kaggle to acquire the dataset on Kaggle. This will hold every play and calculate other features used for analysis. The csv output from this will be used to join with the openness calculation.

implement.ipynb - This notebook creates the Random Forest used to predict target probability. It takes the csv from findPlayersWithTargets.ipynb then joins it to the openness data. In the end, it binds the results so they can be used for analysis. It also creates a dataframe of who each QB was on each play, which is used for analysis. This code was run in Google Colab.

summarise_model.ipynb - Joins files from implement.ipynb to create summary tables and dataframes which are exported for data visualization. This code was run in Google Colab.

viz_1.Rmd - creates visualizations from the data created in summarise_model.ipynb.

logisitc_and_viz.Rmd - Creates logistic regression models and visualizations.

dansbot-openness.ipynb - Takes the week data csv's and calculates the rectangle around each players. The rectangles are then used to calculate the "openness" for each eligible receiver. After openness is calculated the resulting dataframe is saved as output to be used for algs that require openness as a parameter. This notebook also creates images for defined plays that show the players on a football field, their rectangle, and the openness of receivers. These images can be used to make gifs that show the play in real time.

make_gifs.py - Uses the images output from dansbot-openness.ipynb to create gifs that show plays in real time.

## EXECUTION

#### Openness Calculation and Gif Generator
```shell
pip install -r requirements.txt
```

dansbot-openness.ipynb is run in a jupyter notebook. When running in the Kaggle environment, set the in_kaggle flag found in cell 3 to True. Choose the csv file to create the dataframe by changing the csv_fn in cell 3. Then Run All Cells. The resulting outputs will be a .pickle file of the created dataframe that includes the player rectangles and openness.

#####(This can only be run after dansbot-openness.ipynb is executed.)
```shell
python make_gifs.py
```

#### Data Visualization Tool
Make sure both plotly and dash are installed in your environment:

```shell
conda install plotly dash
```

Generate a data directory and place [these](https://gtvault-my.sharepoint.com/:f:/g/personal/jperalta8_gatech_edu/ElvMzTGPGJxLrGTU20HnsCsB6URqdsnnP-rsAfzTuxMj1A?e=yChGBQ) files in it. Execute the app.py file (found in the CODE folder) from a terminal:

```shell
python app.py
```

Open the url highlighted in the output on a web browser. Should looke like  (http://127.0.0.1:8050/)

