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
* atr dev delete test-client 0.3+cli
<.etc.>

$ atr release start test-client 0.3+cli
<.skip.>created<.skip.>

$ atr dev delete test-client 0.3+cli
test-client-0.3+cli

$ atr release start test-client 0.3+cli
<.skip.>created<.skip.>

$ atr config path
<?config_rel_path?>

$ atr upload test-client 0.3+cli atr-client.conf <!config_rel_path!>
<.skip.>created<.skip.>

$ atr check wait test-client 0.3+cli -i 25
Checks completed.

$ atr check status test-client 0.3+cli
Total checks: 1
  warning: 1

$ atr check status test-client 0.3+cli 00002
Total checks: 1
  warning: 1

$ atr vote start test-client 0.3+cli 00002 -m "<!user!>@apache.org"
<.skip.>"email_to":"<!user!>@apache.org"<.skip.>

$ atr vote resolve test-client 0.3+cli failed
Vote marked as failed.

$ atr vote start test-client 0.3+cli 00002 -m "<!user!>@apache.org"
<.skip.>"email_to":"<!user!>@apache.org"<.skip.>

$ atr vote resolve test-client 0.3+cli passed
Vote marked as passed.

$ atr distribution record test-client 0.3+cli NPM None react 18.2.0 False False
Distribution recorded.

$ atr announce test-client 0.3+cli 00003 -m "<!user!>@apache.org" -b "Release test-client 0.3+cli has been announced."
Announcement sent.

<# tidy up #>
* atr dev delete test-client 0.3+cli
<.etc.>
