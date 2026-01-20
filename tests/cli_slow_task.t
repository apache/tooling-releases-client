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

<# delete any existing draft, ignoring errors #>
* atr dev delete test-client 0.3+slow
<.etc.>

$ atr release start test-client 0.3+slow
<.skip.>created<.skip.>

$ atr config path
<?config_rel_path?>

$ atr upload test-client 0.3+slow deliberately_slow_ATR_task_filename.txt <!config_rel_path!>
<.skip.>created<.skip.>

! atr vote start test-client 0.3+slow 00002 -m "<!user!>@apache.org"
<.stderr.>
atr: error: Error message from the API:
400 https://localhost.apache.org:8080/api/vote/start
{
  "error": "All checks must be completed before starting a vote"
}

<# tidy up #>
* atr dev delete test-client 0.3+slow
<.etc.>
