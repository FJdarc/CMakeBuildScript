PS C:\dev\CMakeEasyScript> py .\Ces.py -h
usage: Ces.py [-h] [{x64,x86}] [{d,r}] [{st,sh}] [ProgramName]

CMake cross-platform build script

positional arguments:
  {x64,x86}    Architecture: 'x64' (default) or 'x86'
  {d,r}        Build type: 'd' (Debug, default) or 'r' (Release)
  {st,sh}      Library type: 'st' (Static, default) or 'sh' (Shared)
  ProgramName  Name of the executable to run (default: current directory)

options:
  -h, --help   show this help message and exit

Example: python Ces.py x64 d st Example