$ atr dev env
ATR_CLIENT_CONFIG_PATH="<!CONFIG_PATH!>"
<!...!>

! atr config file
<!stderr!>
atr: error: No configuration file found.

$ atr config path
/<!ROOT_REL_PATH!>

$ atr set asf.uid example
Set asf.uid to "example".

$ atr config file
asf:
  uid: example

! atr drop --path asf.uid
╭─ Error ──────────────────────────────────────────────────────────────────────╮
│ Unknown option: "--path".                                                    │
╰──────────────────────────────────────────────────────────────────────────────╯

$ atr drop asf.uid
Removed asf.uid.

! atr config file
<!stderr!>
atr: error: No configuration file found.
