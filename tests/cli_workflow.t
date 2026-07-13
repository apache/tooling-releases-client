$ atr set atr.host localhost.apache.org:8080
Set atr.host to "localhost.apache.org:8080".

$ atr dev user
<?user?>

$ atr set asf.uid <!user!>
Set asf.uid to "<!user!>".

$ atr dev pat
<?pat?>

$ atr set tokens.pat <!pat!>
Set tokens.pat.

<# delete any existing draft, ignoring errors #>
* atr dev delete test-client 0.3+cli
<.etc.>

$ atr release start test-client 0.3+cli
<.skip.>created<.skip.>

$ atr dev delete test-client 0.3+cli
test-client-0.3+cli

$ atr release start test-client 0.3+cli
<.skip.>created<.skip.>

<# associate the test signing key with the test committee, tolerating errors #>
* atr key add ATR_Test_0x1913BD07F118B758_public.asc test
<.etc.>

$ atr upload test-client 0.3+cli apache-test-0.2.tar.gz apache-test-0.2.tar.gz
Upload quarantined pending archive validation.
<.skip.>created<.skip.>

$ atr upload test-client 0.3+cli apache-test-0.2.tar.gz.sha512 apache-test-0.2.tar.gz.sha512
<.skip.>created<.skip.>

$ atr upload test-client 0.3+cli apache-test-0.2.tar.gz.asc apache-test-0.2.tar.gz.asc
<.skip.>created<.skip.>

$ atr check wait test-client 0.3+cli -i 25
Checks completed.

$ atr check status test-client 0.3+cli
Total checks: <.skip.>
<.etc.>

$ atr check status test-client 0.3+cli 00004
Total checks: <.skip.>
<.etc.>

<# supply a literal body while omitting the subject and duration to exercise their server-side defaults #>
$ atr vote start test-client 0.3+cli 00004 -m "<!user!>@apache.org" -b "Vote body supplied as literal text." --concerns-noted atr.tasks.checks.rat.check
<.skip.>"email_to":"<!user!>@apache.org"<.skip.>

$ atr vote resolve test-client 0.3+cli failed
Vote marked as failed.

$ atr vote start test-client 0.3+cli 00004 -m "<!user!>@apache.org" --concerns-noted atr.tasks.checks.rat.check
<.skip.>"email_to":"<!user!>@apache.org"<.skip.>

$ atr vote resolve test-client 0.3+cli passed
Vote marked as passed.

$ atr distribution record test-client 0.3+cli NPM None react 18.2.0 False False
Distribution recorded.

$ atr distribution list test-client 0.3+cli
<.skip.>react@18.2.0<.skip.>

<# omit body to exercise the server-side announce template #>
$ atr announce test-client 0.3+cli 00005 -m "<!user!>@apache.org"
Announcement sent with a body rendered by the server from the project's announce email template.

<# tidy up #>
* atr dev delete test-client 0.3+cli
<.etc.>

<# regression test for atr draft delete #>
<# delete any existing draft, ignoring errors #>
* atr dev delete test-client 0.3+draft
<.etc.>

$ atr release start test-client 0.3+draft
<.skip.>created<.skip.>

$ atr draft delete test-client 0.3+draft
True
