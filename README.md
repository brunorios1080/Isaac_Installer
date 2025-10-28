Simplify the process of using Isaac Sim for designers by providing a single UI that handles installation, updates, and launching — removing the need to manually interact with Nucleus, GitHub, or extension managers.

Before installation (running the executable in the dist folder) run this command on your command prompt to enable long path:

New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force
