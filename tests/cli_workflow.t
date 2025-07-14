$ atr set atr.host 127.0.0.1:8080
Set atr.host to "127.0.0.1:8080".

$ atr dev user
<?user?>

$ atr set asf.uid <!user!>
Set asf.uid to "<!user!>".

$ atr dev pat
<?pat?>

$ atr set tokens.pat <!pat!>
Set tokens.pat to "<!pat!>".

<# Delete any existing draft, ignoring errors. #>
* atr draft delete tooling-test-example 0.3+cli
<.etc.>

$ atr release start tooling-test-example 0.3+cli
<.skip.>created<.skip.>

$ atr config path
<?config_rel_path?>

$ atr upload tooling-test-example 0.3+cli atr-client.conf <!config_rel_path!>
<.skip.>created<.skip.>

$ atr checks wait tooling-test-example 0.3+cli -i 25
Checks completed.

$ atr checks status tooling-test-example 0.3+cli
Total checks: 1
  warning: 1

$ atr vote start tooling-test-example 0.3+cli 00002 -m "<!user!>@apache.org"
<.skip.>"email_to": "<!user!>@apache.org"<.skip.>

$ atr vote resolve tooling-test-example 0.3+cli failed
{"success": "Vote marked as failed"}

$ atr vote start tooling-test-example 0.3+cli 00002 -m "<!user!>@apache.org"
<.skip.>"email_to": "<!user!>@apache.org"<.skip.>

$ atr vote resolve tooling-test-example 0.3+cli passed
{"success": "Vote marked as passed"}

<# Tidy up. #>
* atr dev delete tooling-test-example 0.3+cli
<.etc.>
