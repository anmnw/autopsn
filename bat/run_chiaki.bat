

set chiaki_path=%~dp0..\..\chiaki\chiaki.exe
set nircmdc_path=%~dp0..\..\nircmd\nircmdc.exe

start "" %chiaki_path% 
timeout /t 5
%nircmdc_path% win max process chiaki.exe
