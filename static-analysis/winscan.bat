REM (C) Copyright HCL Technologies Ltd. 2017.  All Rights Reserved.
REM LICENSE: Apache License, Version 2.0 https://www.apache.org/licenses/LICENSE-2.0

REM This script demonstrates some sample usage of the appscan CLI commands in a Windows environment 
REM See: https://www.ibm.com/support/knowledgecenter/en/SSYJJF_1.0.0/ApplicationSecurityonCloud/src_cli_win.html

@ECHO off
SETLOCAL

REM Change these to match your environment 
REM The application ID can be retrived from the "appscan list_apps" command
SET APIKEY_ID="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
SET APIKEY_SECRET="yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy"
SET APPLICATION_ID="zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz"
SET IRX_NAME="myscan.irx"


REM *********       LOG INTO ASOC      *********
ECHO Logging in to ASoC...
CALL appscan api_login -u %APIKEY_ID% -P %APIKEY_SECRET% -persist


REM *********       GENERATE IRX       *********
ECHO Generating IRX file...
CALL appscan prepare -n %IRX_NAME%


REM *********  SUBMIT IRX FOR ANALYSIS *********
ECHO Submitting IRX to ASoC for analysis...
CALL appscan queue_analysis -a %APPLICATION_ID% -f %IRX_NAME% -n %IRX_NAME% > queue_analysis.txt
FOR /f "delims==" %%a IN (queue_analysis.txt) DO SET analysis_job_id=%%a
DEL queue_analysis.txt
ECHO Analysis Job ID = %analysis_job_id%


REM *********    WAIT FOR COMPLETION   *********
ECHO Waiting for analysis to complete...
:LoopStart
CALL appscan status -i %analysis_job_id% > status.txt
FOR /f "delims==" %%a in (status.txt) do set job_status=%%a
DEL status.txt
IF "%job_status%"=="FinishedRunning"           GOTO LoopEnd
IF "%job_status%"=="FinishedRunningWithErrors" GOTO BadScan
IF "%job_status%"=="Ready"                     GOTO LoopEnd
IF "%job_status%"=="ReadyIncomplete"           GOTO BadScan
IF "%job_status%"=="FailedToScan"              GOTO BadScan
IF "%job_status%"=="ManuallyStopped"           GOTO BadScan
REM Wait 30 seconds
PING localhost -n 30 >NUL
GOTO LoopStart

:LoopEnd

REM *********    GET THE REPORT     *********
ECHO Getting the report...
CALL appscan get_result -i %analysis_job_id% -t html


REM *********    GET SCAN DATA      *********
ECHO Scan Information:
CALL appscan info -i %analysis_job_id%
GOTO :EOF


:BadScan
ECHO An Error Occurred during the scan (jobid=%analysis_job_id%)





 






