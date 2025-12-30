@echo off

:: Hit By Pitches run script
:: Author: Hossein Fuller <hossfuller@protonmail.com>
:: Version: 1.0.0

:: Change to the project directory.
cd /d "%~dp0"

:: Set Python path and run the downloader with all command line arguments.
set PYTHONPATH=%cd%
@REM python -m src.hbp.dbpopulator %*
python -m src.hbp.downloader %*
@REM python -m src.hbp.plotter %*
@REM python -m src.hbp.skeeter %*
