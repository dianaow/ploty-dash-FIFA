### Set up instructions

#### Initial Data Processing

1) To create a virtual environment in python 3.9

`virtualenv --python=/usr/bin/python3.9 <path/to/new/virtualenv/>`

2) Activate the environment and install all the packages available in the requirement.txt file.

`source <path/to/new/virtualenv>/bin/activate
pip install -r <path/to/requirement.txt>`

3) To create and store recommendation system algorithm output files (This only needs to be run once)

`python3 __init__.py`