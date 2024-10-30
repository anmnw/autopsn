
REM 获取当前时间
for /f "tokens=1-2 delims=:" %%A in ('time /t') do (
    set HOUR=%%A
    set MINUTE=%%B
)
set HOUR=%time:~0,2%
set MINUTE=%time:~3,2%
REM 去除前导空格（处理单数字小时）
set /a HOUR=%HOUR: =%

REM 实际上是在计算到0360的时间差 
if %HOUR% lss 3 (
    set /a HOURS_LEFT=3 - %HOUR%
) else (
    set /a HOURS_LEFT=24 - %HOUR% + 3
)

set /a MINUTES_LEFT=60 - %MINUTE%



REM 计算总延迟时间（秒）
set /a SECONDS_LEFT=(%HOURS_LEFT%*60 + %MINUTES_LEFT%) * 60

REM 打印计算出的秒数
echo 当前时间距离凌晨4点有 %SECONDS_LEFT% 秒
echo 计算完毕，系统将在该时间后重启。

REM 设置延迟重启
shutdown /r /t %SECONDS_LEFT%
pause
