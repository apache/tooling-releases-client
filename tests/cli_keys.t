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

$ atr key user
<.etc.>

$ atr dev pwd
<.skip.>tmp<.skip.>

<# write a test key to tooling-public-test.asc #>
$ atr dev key

$ atr key add tooling-public-test.asc
E35604DD9E2892E5465B3D8A203F105A7B33A64F

$ atr key get E35604DD9E2892E5465B3D8A203F105A7B33A64F
<.skip.>e35604dd9e2892e5465b3d8a203f105a7b33a64f<.skip.>example.invalid<.skip.>

* atr key delete E35604DD9E2892E5465B3D8A203F105A7B33A64F
<.etc.>

$ atr key upload tooling-public-test.asc tooling
<.etc.>
