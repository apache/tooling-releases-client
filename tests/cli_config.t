$ atr dev env
ATR_CLIENT_CONFIG_PATH="<.skip.>"
<.etc.>

! atr config file
<.stderr.>
atr: error: No configuration file found.

$ atr config path
/<.skip.>

$ atr set asf.uid example
Set asf.uid to "example".

$ atr config file
asf:
  uid: example

! atr drop --path asf.uid
<.skip.>
<.skip.>Unknown option: "--path"<.skip.>
<.etc.>

$ atr drop asf.uid
Removed asf.uid.

! atr config file
<.stderr.>
atr: error: No configuration file found.
