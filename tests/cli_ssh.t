$ atr set atr.host localhost.apache.org:8080
Set atr.host to "localhost.apache.org:8080".

$ atr dev user
<?user?>

$ atr set asf.uid <!user!>
Set asf.uid to "<!user!>".

$ atr dev pat
<?pat?>

$ atr set tokens.pat <!pat!>
Set tokens.pat to "<!pat!>".

$ atr ssh list
<.etc.>

! atr ssh add invalid-key
<.stderr.>
atr: error: Error message from the API:
500 https://localhost.apache.org:8080/api/ssh/add
{
  "error": "Invalid SSH key format"
}

* atr ssh delete SHA256:p/i72djQU2/tmcCOtW6YzLoSVhmaaaQd+2/uaTkbp4M
<.etc.>

$ atr ssh add "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIL63zVyeqQ0jF33V9Uq+R0cmsgZC8RoG9yZoe3Zap0Xl testing-key"
SHA256:p/i72djQU2/tmcCOtW6YzLoSVhmaaaQd+2/uaTkbp4M

$ atr ssh list
<.skip.>SHA256:p/i72djQU2/tmcCOtW6YzLoSVhmaaaQd+2/uaTkbp4M<.skip.>

* atr ssh delete SHA256:p/i72djQU2/tmcCOtW6YzLoSVhmaaaQd+2/uaTkbp4M
<.etc.>
