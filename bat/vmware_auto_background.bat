set nircmdc_path=%~dp0..\..\nircmd\nircmdc.exe
%nircmdc_path% win hide process "cmd.exe"
%nircmdc_path% exec hide "%~dp0vmware_auto.bat"
pause