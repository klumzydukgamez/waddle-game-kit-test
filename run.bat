@echo off

if not exist build_out exit

cd build_out
cls

if not exist index.html exit

emrun --no_emrun_detect index.html

pause
cd ..
cls

