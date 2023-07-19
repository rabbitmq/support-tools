param(
    [switch]$Debug = $false,
    [switch]$Verbose = $false,
    [int]$DebugLevel = 0,
    [int]$VerboseLevel = 0,
    [int]$OutputWidth = 8192
)

## -------------------------------------------------------------------
##
## rabbitmq-collect-env.ps1:
## Collect artifacts for RabbitMQ troubleshooting on Windows systems
##
## Based on `riak-debug' as developed by Basho Technologies, Inc
##
## Copyright (c) 2017 Basho Technologies, Inc.  All Rights Reserved.
## Copyright (c) 2007-2023 VMware, Inc. or its affiliates.  All rights reserved.
##
## This file is provided to you under the Apache License,
## Version 2.0 (the "License"); you may not use this file
## except in compliance with the License.  You may obtain
## a copy of the License at
##
##   https://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing,
## software distributed under the License is distributed on an
## "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
## KIND, either express or implied.  See the License for the
## specific language governing permissions and limitations
## under the License.
##
## -------------------------------------------------------------------

$ErrorActionPreference = 'Stop'

if ($Debug)
{
    $DebugPreference = 'Continue'
    Write-Debug -Message 'Enabling debug output'
    if ($DebugLevel -gt 0)
    {
        Set-PSDebug -Strict -Trace 1
    }
}
else
{
    $DebugPreference = 'SilentlyContinue'
    Set-PSDebug -Off
}

if ($Verbose)
{
    $VerbosePreference = 'Continue'
    Write-Verbose -Message 'Enabling verbose output'
}
else
{
    $VerbosePreference = 'SilentlyContinue'
}

Set-StrictMode -Version Latest -ErrorAction 'Stop'

function New-TemporaryDirectory
{
    New-Variable -Name parent -Option Constant -Value ([System.IO.Path]::GetTempPath())
    Do
    {
        $tmpDir = New-Item -ItemType Directory -Path (Join-Path -Path $parent -ChildPath (New-Guid))
    }
    While (-Not $tmpDir)

    return $tmpDir
}

function Run-Init
{
    New-Variable -Name startTimeUTC -Option Constant -Value ((Get-Date).ToUniversalTime()).ToString("yyyyMMddTHHmmssZ")

    $startMsg = "START TIME UTC: $startTimeUTC"
    Write-Verbose -Message $startMsg

    New-Variable -Name curdir -Scope Script -Option Constant -Value $PSScriptRoot
    Write-Verbose -Message "curdir: $curdir"

    New-Variable -Name outputFile -Scope Script -Option Constant -Value `
        $(Join-Path -Path $curdir -ChildPath "rabbitmq-collect-env-output-$startTimeUTC.txt")
    Write-Verbose -Message "outputFile: $outputFile"

    New-Variable -Name logsArchiveFile -Scope Script -Option Constant -Value `
        $(Join-Path -Path $curdir -ChildPath "rabbitmq-collect-env-logs-$startTimeUTC.zip")
    Write-Verbose -Message "logsArchiveFile: $logsArchiveFile"

    $initOutFileArgs = @{
        Append = $true
        FilePath = $outputFile
        Width = $OutputWidth
        Encoding = 'UTF8'
    }
    if ($VerboseLevel -gt 0) {
        $initOutFileArgs += @{
            Verbose = $true
        }
    } else {
        $initOutFileArgs += @{
            Verbose = $false
        }
    }
    New-Variable -Name outFileArgs -Scope Script -Option Constant -Value $initOutFileArgs 

    $initAddContentArgs = @{
        Path = $outputFile
    }
    if ($VerboseLevel -gt 0) {
        $initAddContentArgs += @{
            Verbose = $true
        }
    } else {
        $initAddContentArgs += @{
            Verbose = $false
        }
    }
    New-Variable -Name addContentArgs -Scope Script -Option Constant -Value $initAddContentArgs 

    New-Variable -Name sep -Scope Script -Option Constant -Value '------------------------------------------------------------------------------------------------------------------------------------'

    Remove-Item -ErrorAction 'SilentlyContinue' -Force -LiteralPath $outputFile

    Add-Content @addContentArgs -Value "$sep$([Environment]::NewLine)$startMsg"
}

function Get-ErlangInfo
{
    $msg = 'Erlang information'
    Write-Verbose -Message $msg
    Add-Content @addContentArgs -Value "$sep$([Environment]::NewLine)$msg$([Environment]::NewLine)"

    New-Variable -Name erts_version -Option Constant `
        -Value (Get-ChildItem -LiteralPath HKLM:\SOFTWARE\WOW6432Node\Ericsson\Erlang | Select-Object -Last 1).PSChildName

    New-Variable -Name erlangProgramFilesPath -Option Constant `
        -Value ((Get-ItemProperty -LiteralPath HKLM:\SOFTWARE\WOW6432Node\Ericsson\Erlang\$erts_version).'(default)')

    New-Variable -Name erl_exe -Option Constant `
        -Value (Join-Path -Path $erlangProgramFilesPath -ChildPath 'bin' | Join-Path -ChildPath 'erl.exe')

    New-Variable -Name otp_version -Option Constant `
        -Value $(& $erl_exe -boot no_dot_erlang -noshell -eval "{ok,Version}=file:read_file(filename:join([code:root_dir(),'releases',erlang:system_info(otp_release),'OTP_VERSION'])),io:fwrite(Version),halt().")

    $msg = "otp_version: $otp_version"
    Write-Verbose -Message $msg
    Add-Content @addContentArgs -Value $msg

    $msg = "erts_version: $erts_version"
    Write-Verbose -Message $msg
    Add-Content @addContentArgs -Value $msg

    $msg = "erlangProgramFilesPath: $erlangProgramFilesPath"
    Write-Verbose -Message $msg
    Add-Content @addContentArgs -Value $msg

    $msg = "erl_exe: $erl_exe"
    Write-Verbose -Message $msg
    Add-Content @addContentArgs -Value $msg
}

function Get-RabbitMQInfo
{
    $msg = 'RabbitMQ information'
    Write-Verbose -Message $msg
    Add-Content @addContentArgs -Value "$sep$([Environment]::NewLine)$msg$([Environment]::NewLine)"

    New-Variable -Name rmqInstallDir -Option Constant `
        -Value (Resolve-Path -LiteralPath (Get-ItemProperty -Name Install_Dir -LiteralPath 'HKLM:\SOFTWARE\WOW6432Node\VMware, Inc.\RabbitMQ Server').Install_Dir)

    $msg = "RabbitMQ installation directory: $rmqInstallDir"
    Write-Verbose -Message $msg
    Add-Content @addContentArgs -Value $msg

    New-Variable -Name rmqServerDir -Option Constant `
        -Value (Resolve-Path -LiteralPath (Get-ChildItem -LiteralPath $rmqInstallDir -Filter 'rabbitmq_server-*' | Select-Object -First 1).FullName)
    $msg = "RabbitMQ server installation directory: $rmqServerDir"
    Write-Verbose -Message $msg
    Add-Content @addContentArgs -Value $msg

    New-Variable -Name rmqServerSbinDir -Option Constant `
        -Value (Resolve-Path -LiteralPath (Join-Path -Path $rmqServerDir.Path -ChildPath 'sbin'))
    $msg = "RabbitMQ server sbin directory: $rmqServerSbinDir"
    Write-Verbose -Message $msg
    Add-Content @addContentArgs -Value $msg

    New-Variable -Name rmqEnvBat -Option Constant `
        -Value (Resolve-Path -LiteralPath (Join-Path -Path $rmqServerSbinDir.Path -ChildPath 'rabbitmq-env.bat'))
    $msg = "RabbitMQ environment batch file: $rmqEnvBat"
    Add-Content @addContentArgs -Value $msg

    New-Variable -Name rabbitmqctl -Option Constant `
        -Value (Resolve-Path -LiteralPath (Join-Path -Path $rmqServerSbinDir.Path -ChildPath 'rabbitmqctl.bat'))
    $msg = "RabbitMQ rabbitmqctl.bat command: $($rabbitmqctl.Path)"
    Write-Verbose -Message $msg
    Add-Content @addContentArgs -Value $msg

    ########################################################################
    # Get RabbitMQ configuration from rabbit_prelaunch
    #
    $tmpFile = New-TemporaryFile
    $tmpFileName = $tmpFile.FullName -replace '\\','/'
    try
    {
        $msg = 'COMMAND / CONFIG: rabbitmqctl.bat eval rabbit_prelaunch:get_context/0'
        Write-Verbose -Message $msg
        Add-Content @addContentArgs -Value "$sep$([Environment]::NewLine)$msg"

        $evalString = '"C=rabbit_prelaunch:get_context(),Keys=[advanced_config_file,conf_env_file,config_base_dir,data_base_dir,data_dir,enabled_plugins_file,home_dir,log_base_dir,main_config_file,main_log_file,quorum_queue_dir,rabbitmq_base,rabbitmq_home,stream_queue_dir],file:write_file(""' + $tmpFileName + '"",rabbit_json:encode([{K,unicode:characters_to_binary(maps:get(K,C))} || K <- Keys]))."'
        & $rabbitmqctl eval $evalString | Out-Null

        New-Variable -Name rmqConfigJson -Option Constant -Value (Get-Content -LiteralPath $tmpFile | ConvertFrom-Json)
        $rmqConfigJson | Out-File @outFileArgs
        Write-Verbose -Message $rmqConfigJson
    }
    finally
    {
        Remove-Item -ErrorAction 'SilentlyContinue' -Force $tmpFile
    }

    ########################################################################
    # Get RabbitMQ log files
    #
    $msg = 'COMMAND: getting RabbitMQ log files'
    Write-Verbose -Message $msg
    Add-Content @addContentArgs -Value "$sep$([Environment]::NewLine)$msg"
    New-Variable -Name rmqLogBaseDir -Option Constant -Value $rmqConfigJson.log_base_dir
    New-Variable -Name rmqMainLogFileFullName -Option Constant -Value $rmqConfigJson.main_log_file
    New-Variable -Name rmqMainLogFileShortName -Option Constant -Value (Split-Path -Leaf -Resolve $rmqMainLogFileFullName)
    New-Variable -Name rmqMainLogFileFullNameTempParent -Option Constant -Value (New-TemporaryDirectory)
    New-Variable -Name rmqMainLogFileFullNameTemp -Option Constant -Value (Join-Path -Path $rmqMainLogFileFullNameTempParent -ChildPath $rmqMainLogFileShortName)
    if (Test-Path -Path $rmqLogBaseDir)
    {
        try
        {
            # Note:
            # The combination of -Exclude and -LiteralPath does NOT work correctly using Powershell 5.1
            Get-ChildItem -Recurse -Path $rmqLogBaseDir -Exclude $rmqMainLogFileShortName | Compress-Archive -Force -DestinationPath $logsArchiveFile
            Copy-Item -Force -LiteralPath $rmqMainLogFileFullName -Destination $rmqMainLogFileFullNameTemp
            Compress-Archive -LiteralPath $rmqMainLogFileFullNameTemp -Update -DestinationPath $logsArchiveFile
        }
        finally
        {
            Remove-Item -Recurse -Force -ErrorAction 'SilentlyContinue' -LiteralPath $rmqMainLogFileFullNameTempParent
        }
    }
    else
    {
        $msg = "[ERROR] RabbitMQ log base dir does not exist: $rmqLogBaseDir"
        Write-Error -ErrorAction 'Continue' -Message $msg
        Add-Content @addContentArgs -Value $msg
    }

    ########################################################################
    # rabbitmq-env.bat (runs rabbitmq-env-conf.bat if it exists)
    #
    if (Test-Path -Path $rmqEnvBat)
    {
        New-Variable -Name rabbitmqEnvRunnerTmpl -Option Constant -Value @"
@echo off
setlocal
setlocal enabledelayedexpansion
setlocal enableextensions
if ERRORLEVEL 1 (
    echo "Failed to enable command extensions!"
    exit /B 1
)
call "@@PATH@@"
set
"@
        $tmpFile = New-TemporaryFile
        $rabbitmqEnvRunner = "$tmpFile.bat"
        Move-Item -Force -LiteralPath $tmpFile -Destination $rabbitmqEnvRunner
        try
        {
            Set-Content -LiteralPath $rabbitmqEnvRunner -Value $($rabbitmqEnvRunnerTmpl -replace '@@PATH@@', $rmqEnvBat.Path)
            $msg = "COMMAND: rabbitmq-env.bat"
            Write-Verbose -Message $msg
            Add-Content @addContentArgs -Value "$sep$([Environment]::NewLine)$msg$([Environment]::NewLine)"
            & $rabbitmqEnvRunner | Out-File @outFileArgs
        }
        finally
        {
            Remove-Item -ErrorAction 'SilentlyContinue' -Force $tmpFile
            Remove-Item -ErrorAction 'SilentlyContinue' -Force $rabbitmqEnvRunner
        }
    }
    else
    {
        $msg = "[ERROR] could not find expected RabbitMQ environment batch file: $rmqEnvBatFullName"
        Write-Error -ErrorAction 'Continue' -Message $msg
        Add-Content @addContentArgs -Value $msg
    }

    $msg = "COMMAND: rabbitmqctl.bat report"
    Write-Verbose -Message $msg
    Add-Content @addContentArgs -Value "$sep$([Environment]::NewLine)$msg$([Environment]::NewLine)"
    & $rabbitmqctl report | ForEach-Object { $_ -replace '\x1b\[[0-9;]*m','' } | Out-File @outFileArgs
}

function Get-Win32_OperatingSystem
{
    $msg = 'COMMAND: "Get-CimInstance Win32_OperatingSystem"'
    Write-Verbose -Message $msg
    Add-Content @addContentArgs -Value "$sep$([Environment]::NewLine)$msg"
    Get-CIMInstance Win32_OperatingSystem | Format-List -Property '*' | Out-File @outFileArgs
}

function Get-Win32_Process
{
    $msg = 'COMMAND: "Get-CimInstance Win32_Process | Select-Object -Property Name,WorkingSetSize,Path,CommandLine"'
    Write-Verbose -Message $msg
    Add-Content @addContentArgs -Value "$sep$([Environment]::NewLine)$msg"
    Get-CimInstance Win32_Process | Select-Object -Property Name,WorkingSetSize,CommandLine | Sort-Object -Property Name | Format-List | Out-File @outFileArgs
}

function Get-Win32_Services
{
    $msg = 'COMMAND: "Get-Service -ErrorAction ''SilentlyContinue'' | Where-Object { $_.Status -eq ''Running'' } | Select-Object -Property Name,Description,BinaryPathName"'
    Write-Verbose -Message $msg
    Add-Content @addContentArgs -Value "$sep$([Environment]::NewLine)$msg"
    Get-Service -ErrorAction 'SilentlyContinue' | Where-Object { $_.Status -eq 'Running' } | Select-Object -Property Name,Description,BinaryPathName | Format-List | Out-File @outFileArgs
}

function Run-Main
{
    Get-ErlangInfo
    Get-RabbitMQInfo
    Get-Win32_OperatingSystem
    Get-Win32_Process
    Get-Win32_Services
}

function Run-End
{
    New-Variable -Name stopTimeUTC -Option Constant -Value ((Get-Date).ToUniversalTime()).ToString("yyyyMMddTHHmmssZ")
    $msg = "STOP TIME UTC: $stopTimeUTC"
    Write-Verbose -Message $msg
    Add-Content @addContentArgs -Value "$sep$([Environment]::NewLine)$msg"
}

try
{
    Run-Init
    Run-Main
    Run-End
}
finally
{
    Set-PSDebug -Off
}
