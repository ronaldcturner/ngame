' NGAME — silent dashboard start for the Windows Startup folder.
' Prefer a shortcut to this file in shell:startup (avoids a flashing console).
' This script must live next to start-dashboard.bat at the repository root.
Option Explicit
Dim sh, fso, root, bat
Set fso = CreateObject("Scripting.FileSystemObject")
root = fso.GetParentFolderName(WScript.ScriptFullName)
bat = root & "\start-dashboard.bat"
If Not fso.FileExists(bat) Then
  MsgBox "NGAME: start-dashboard.bat not found next to start-dashboard-silent.vbs." & vbCrLf & root, vbCritical, "NGAME"
  WScript.Quit 1
End If
Set sh = CreateObject("WScript.Shell")
' WindowStyle 0 = hidden; False = do not wait for the bat to finish
sh.Run """" & bat & """", 0, False
