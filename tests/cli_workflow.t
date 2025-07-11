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

<# Reset any existing draft, ignoring errors. #>
* atr draft delete tooling-test-example 0.3+cli
<.etc.>

$ atr release start tooling-test-example 0.3+cli
<.skip.>created<.skip.>
