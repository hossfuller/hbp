# hbp

Find's the MLB HBP events and posts them to Bluesky.


<!-- --------------------------------------------------------------------------- -->


<div id='setting_up_the_virtual_environment' />

## Setting up the virtual environment

From start to finish, here's what to do for the different platforms after cloning this repository.


<div id='setup_summary_linux' />

#### Linux

If Debian/Ubuntu:

```sh
sudo apt-get install python3.13 python3.13-venv python3-pip
```

If RHELx:

```sh
sudo apt-get install python3 python3-venv python3-pip
```

Then, for both:

```sh
python3.13 -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install pipreqs black mypy
python -m  pipreqs.pipreqs . --force --ignore ".venv"
pip install -r requirements.txt
```


<div id='setup_summary_windows' />

#### Windows 11

How do you install python on Windows 11?

```sh
python -m venv env
.\env\bin\Activate.ps1  ## or .\env\Scripts\Activate.ps1

python -m pip install --upgrade pip
python -m pip install pipreqs black mypy
python -m  pipreqs.pipreqs . --force --ignore "env"
pip install -r requirements.txt
```

**NOTE:** See that `"env"` on the `--ignore` flag? That may not be necessary for Windows, but if there's a `UnicodeDecodeError` error when running `pipreqs`, you'll need to add that flag to avoid the error.


<!-- --------------------------------------------------------------------------- -->


<div id='set_up_bluesky_credentials' />

## Set up Bluesky credentials

Create a file called `config/credentials.txt` with only the bluesky account's password. 



<!-- --------------------------------------------------------------------------- -->


## TO-DO

- [x] Move `libhbp` to the main `src/hbp` directory.
- [x] Break the `downloader.py` script into `dbpopulator.py` and `downloader.py` scripts.
- [x] New `downloader.py` script should update the database when it downloads a video.
- [ ] How do I pass a keyboard interrupt through a `.bat`/`.sh` script to the main python executable?
- [ ] Make `SQLiteManager` receive a `create table` query so I don't have to make edits in the class itself.
- [ ] Store the `CREATE TABLE` in the constants.py file.
- [ ] Put a normalized batter's silhouette on plots to add more context.


<!-- --------------------------------------------------------------------------- -->


## Inspirations

- [coperyan/mlb-videos](https://github.com/coperyan/mlb-videos)
- [dylandru/BSav_Scraper_Vid](https://github.com/dylandru/BSav_Scraper_Vid)
- [Smerity/all_examples_from_bluesky_atproto_python_api.py.txt](https://gist.github.com/Smerity/f896e0a9d27c725b2bc03cd85e105b31)

