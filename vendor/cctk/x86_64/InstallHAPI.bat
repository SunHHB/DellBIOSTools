rem DELL PROPRIETARY INFORMATION
rem
rem This software is confidential.  Dell Inc., or one of its subsidiaries, has supplied this
rem software to you under the terms of a license agreement,nondisclosure agreement or both.
rem You may not copy, disclose, or use this software except in accordance with those terms.
rem
rem Copyright 2020 Dell Inc. or its subsidiaries.  All Rights Reserved.
rem
rem DELL INC. MAKES NO REPRESENTATIONS OR WARRANTIES ABOUT THE SUITABILITY OF THE SOFTWARE,
rem EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED WARRANTIES OF
rem MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, OR NON-INFRINGEMENT.
rem DELL SHALL NOT BE LIABLE FOR ANY DAMAGES SUFFERED BY LICENSEE AS A RESULT OF USING,
rem MODIFYING OR DISTRIBUTING THIS SOFTWARE OR ITS DERIVATIVES.

@echo off

if defined programfiles(x86) (
	call %0%\..\x86_64\HAPI\HAPIInstall.bat
) else (
	call %0%\..\x86\HAPI\HAPIInstall.bat
)	


