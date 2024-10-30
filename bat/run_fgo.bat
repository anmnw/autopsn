set nircmdc_path=%~dp0..\..\nircmd\nircmdc.exe
set memuc_path="C:\Program Files\Microvirt\MEmu\memuc.exe"
set adb_path="C:\Program Files\Microvirt\MEmu\adb.exe"
start "" %chiaki_path% 
%memuc_path% start -i 0
timeout /t 30
%nircmdc_path% win min process Memu.exe
timeout /t 1

%nircmdc_path% win max process Memu.exe

%adb_path% shell am start -a android.intent.action.MAIN -c android.intent.category.LAUNCHER -c android.intent.category.LEANBACK_LAUNCHER  -n com.bilibili.fatego/.EmptyClass
