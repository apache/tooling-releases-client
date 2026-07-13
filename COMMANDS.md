
# atr

```
Usage: atr COMMAND

╭─ Commands ───────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ announce      Announce a release.                                                                                    │
│ api           API operations.                                                                                        │
│ check         Check result operations.                                                                               │
│ config        Configuration operations.                                                                              │
│ dev           Developer operations.                                                                                  │
│ distribution  Distribution operations.                                                                               │
│ docs          Show comprehensive CLI documentation in Markdown.                                                      │
│ draft         Draft operations.                                                                                      │
│ drop          Remove a configuration key using dot notation.                                                         │
│ ignore        Ignore operations.                                                                                     │
│ jwt           JWT operations.                                                                                        │
│ key           Key operations.                                                                                        │
│ list          List all files within a release.                                                                       │
│ release       Release operations.                                                                                    │
│ revisions     List all revisions for a release.                                                                      │
│ rsync         Rsync a release.                                                                                       │
│ set           Set a configuration value using dot notation.                                                          │
│ show          Show a configuration value using dot notation.                                                         │
│ ssh           SSH operations.                                                                                        │
│ upload        Upload a file to a release.                                                                            │
│ verify        Verify an artifact.                                                                                    │
│ vote          Vote operations.                                                                                       │
│ --help (-h)   Display this message and exit.                                                                         │
│ --version     Display application version.                                                                           │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

## atr announce

```
Usage: atr announce --mailing-list STR [OPTIONS] PROJECT VERSION [ARGS]

Announce a release.

╭─ Arguments ──────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *  PROJECT  [required]                                                                                               │
│ *  VERSION  [required]                                                                                               │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Parameters ─────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│    REVISION --revision                                                                                               │
│ *  --mailing-list -m    [required]                                                                                   │
│    --body -b                                                                                                         │
│    --path-suffix -p                                                                                                  │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

## atr api

```
Usage: atr api COMMAND

API operations.

╭─ Commands ───────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ get   GET a resource from the API.                                                                                   │
│ post  POST a resource to the API.                                                                                    │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

### atr api get

```
Usage: atr api get PATH

GET a resource from the API.

╭─ Parameters ─────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *  PATH --path  [required]                                                                                           │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

### atr api post

```
Usage: atr api post [OPTIONS] PATH

POST a resource to the API.

╭─ Arguments ──────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *  PATH  [required]                                                                                                  │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Parameters ─────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --[KEYWORD]                                                                                                          │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

## atr check

```
Usage: atr check COMMAND

Check result operations.

╭─ Commands ───────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ blockers     Get check blockers for the latest or specified release revision.                                        │
│ concerns     Get check concerns for the latest or specified release revision.                                        │
│ exceptions   Get check exceptions for the latest or specified release revision.                                      │
│ notes        Get check notes for the latest or specified release revision.                                           │
│ status       Get check status for a release revision.                                                                │
│ suggestions  Get check suggestions for the latest or specified release revision.                                     │
│ wait         Wait for checks to be completed.                                                                        │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

### atr check blockers

```
Usage: atr check blockers PROJECT VERSION [ARGS]

Get check blockers for the latest or specified release revision.

╭─ Arguments ──────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *  PROJECT  [required]                                                                                               │
│ *  VERSION  [required]                                                                                               │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Parameters ─────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ REVISION --revision                                                                                                  │
│ MEMBERS --members -m --no-members  [default: False]                                                                  │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

### atr check concerns

```
Usage: atr check concerns PROJECT VERSION [ARGS]

Get check concerns for the latest or specified release revision.

╭─ Arguments ──────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *  PROJECT  [required]                                                                                               │
│ *  VERSION  [required]                                                                                               │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Parameters ─────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ REVISION --revision                                                                                                  │
│ MEMBERS --members -m --no-members  [default: False]                                                                  │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

### atr check exceptions

```
Usage: atr check exceptions PROJECT VERSION [ARGS]

Get check exceptions for the latest or specified release revision.

╭─ Arguments ──────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *  PROJECT  [required]                                                                                               │
│ *  VERSION  [required]                                                                                               │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Parameters ─────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ REVISION --revision                                                                                                  │
│ MEMBERS --members -m --no-members  [default: False]                                                                  │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

### atr check notes

```
Usage: atr check notes PROJECT VERSION [ARGS]

Get check notes for the latest or specified release revision.

╭─ Arguments ──────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *  PROJECT  [required]                                                                                               │
│ *  VERSION  [required]                                                                                               │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Parameters ─────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ REVISION --revision                                                                                                  │
│ MEMBERS --members -m --no-members  [default: False]                                                                  │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

### atr check status

```
Usage: atr check status PROJECT VERSION [ARGS]

Get check status for a release revision.

╭─ Arguments ──────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *  PROJECT  [required]                                                                                               │
│ *  VERSION  [required]                                                                                               │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Parameters ─────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ REVISION --revision                                                                                                  │
│ VERBOSE --verbose -v --no-verbose  [default: False]                                                                  │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

### atr check suggestions

```
Usage: atr check suggestions PROJECT VERSION [ARGS]

Get check suggestions for the latest or specified release revision.

╭─ Arguments ──────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *  PROJECT  [required]                                                                                               │
│ *  VERSION  [required]                                                                                               │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Parameters ─────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ REVISION --revision                                                                                                  │
│ MEMBERS --members -m --no-members  [default: False]                                                                  │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

### atr check wait

```
Usage: atr check wait PROJECT VERSION [ARGS]

Wait for checks to be completed.

╭─ Arguments ──────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *  PROJECT  [required]                                                                                               │
│ *  VERSION  [required]                                                                                               │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Parameters ─────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ REVISION --revision                                                                                                  │
│ TIMEOUT --timeout -t    [default: 60]                                                                                │
│ INTERVAL --interval -i  [default: 500]                                                                               │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

## atr config

```
Usage: atr config COMMAND

Configuration operations.

╭─ Commands ───────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ file  Display the configuration file contents.                                                                       │
│ path  Show the configuration file path.                                                                              │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

### atr config file

```
Usage: atr config file

Display the configuration file contents.
```

### atr config path

```
Usage: atr config path

Show the configuration file path.
```

## atr dev

```
Usage: atr dev COMMAND

Developer operations.

╭─ Commands ───────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ delete  Delete a release.                                                                                            │
│ env     Show the environment variables.                                                                              │
│ key     Return a test OpenPGP key.                                                                                   │
│ pat     Read a PAT from development configuration.                                                                   │
│ pwd     Show the current working directory.                                                                          │
│ stamp   Update version and exclude-newer in pyproject.toml.                                                          │
│ token   Generate a random alphabetical token.                                                                        │
│ user    Show the value of $USER.                                                                                     │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

### atr dev delete

```
Usage: atr dev delete PROJECT VERSION

Delete a release.

╭─ Arguments ──────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *  PROJECT  [required]                                                                                               │
│ *  VERSION  [required]                                                                                               │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

### atr dev env

```
Usage: atr dev env

Show the environment variables.
```

### atr dev key

```
Usage: atr dev key

Return a test OpenPGP key.
```

### atr dev pat

```
Usage: atr dev pat

Read a PAT from development configuration.
```

### atr dev pwd

```
Usage: atr dev pwd

Show the current working directory.
```

### atr dev stamp

```
Usage: atr dev stamp

Update version and exclude-newer in pyproject.toml.
```

### atr dev token

```
Usage: atr dev token

Generate a random alphabetical token.
```

### atr dev user

```
Usage: atr dev user

Show the value of $USER.
```

## atr distribution

```
Usage: atr distribution COMMAND

Distribution operations.

╭─ Commands ───────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ list    List recorded distributions for a release.                                                                   │
│ record  Record a distribution.                                                                                       │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

### atr distribution list

```
Usage: atr distribution list PROJECT VERSION

List recorded distributions for a release.

╭─ Arguments ──────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *  PROJECT  [required]                                                                                               │
│ *  VERSION  [required]                                                                                               │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

### atr distribution record

```
Usage: atr distribution record PROJECT VERSION PLATFORM DISTRIBUTION-OWNER-NAMESPACE DISTRIBUTION-PACKAGE 
DISTRIBUTION-VERSION STAGING DETAILS

Record a distribution.

╭─ Parameters ─────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *  PROJECT --project                 [required]                                                                      │
│ *  VERSION --version                 [required]                                                                      │
│ *  PLATFORM --platform               [required]                                                                      │
│ *  DISTRIBUTION-OWNER-NAMESPACE      [required]                                                                      │
│      --distribution-owner-namespace                                                                                  │
│ *  DISTRIBUTION-PACKAGE              [required]                                                                      │
│      --distribution-package                                                                                          │
│ *  DISTRIBUTION-VERSION              [required]                                                                      │
│      --distribution-version                                                                                          │
│ *  STAGING --staging --no-staging    [required]                                                                      │
│ *  DETAILS --details --no-details    [required]                                                                      │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

## atr docs

```
Usage: atr docs

Show comprehensive CLI documentation in Markdown.
```

## atr draft

```
Usage: atr draft COMMAND

Draft operations.

╭─ Commands ───────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ delete  Delete a draft release.                                                                                      │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

### atr draft delete

```
Usage: atr draft delete PROJECT VERSION

Delete a draft release.

╭─ Arguments ──────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *  PROJECT  [required]                                                                                               │
│ *  VERSION  [required]                                                                                               │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

## atr drop

```
Usage: atr drop PATH

Remove a configuration key using dot notation.

╭─ Arguments ──────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *  PATH  [required]                                                                                                  │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

## atr ignore

```
Usage: atr ignore COMMAND

Ignore operations.

╭─ Commands ───────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ add     Add a check ignore.                                                                                          │
│ delete  Delete a check ignore.                                                                                       │
│ list    List check ignores.                                                                                          │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

### atr ignore add

```
Usage: atr ignore add PROJECT [ARGS]

Add a check ignore.

╭─ Arguments ──────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *  PROJECT  [required]                                                                                               │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Parameters ─────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ RELEASE --release                                                                                                    │
│ REVISION --revision                                                                                                  │
│ CHECKER --checker                                                                                                    │
│ PRIMARY-REL-PATH --primary-rel-path                                                                                  │
│ MEMBER-REL-PATH --member-rel-path                                                                                    │
│ STATUS --status                      [choices: concern, exception, suggestion]                                       │
│ MESSAGE --message                                                                                                    │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

### atr ignore delete

```
Usage: atr ignore delete PROJECT ID

Delete a check ignore.

╭─ Arguments ──────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *  PROJECT  [required]                                                                                               │
│ *  ID       [required]                                                                                               │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

### atr ignore list

```
Usage: atr ignore list COMMITTEE

List check ignores.

╭─ Arguments ──────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *  COMMITTEE  [required]                                                                                             │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

## atr jwt

```
Usage: atr jwt COMMAND

JWT operations.

╭─ Commands ───────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ dump     Show decoded JWT payload from stored config.                                                                │
│ info     Show JWT payload in human-readable form.                                                                    │
│ refresh  Fetch a JWT using the stored PAT and store it in config.                                                    │
│ show     Show stored JWT token.                                                                                      │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

### atr jwt dump

```
Usage: atr jwt dump

Show decoded JWT payload from stored config.
```

### atr jwt info

```
Usage: atr jwt info

Show JWT payload in human-readable form.
```

### atr jwt refresh

```
Usage: atr jwt refresh [ARGS]

Fetch a JWT using the stored PAT and store it in config.

╭─ Parameters ─────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ ASF-UID --asf-uid                                                                                                    │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

### atr jwt show

```
Usage: atr jwt show

Show stored JWT token.
```

## atr key

```
Usage: atr key COMMAND

Key operations.

╭─ Commands ───────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ add     Add an OpenPGP key.                                                                                          │
│ delete  Delete an OpenPGP key.                                                                                       │
│ get     Get an OpenPGP key.                                                                                          │
│ upload  Upload a KEYS file.                                                                                          │
│ user    List OpenPGP keys for a user.                                                                                │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

### atr key add

```
Usage: atr key add PATH [ARGS]

Add an OpenPGP key.

╭─ Arguments ──────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *  PATH        [required]                                                                                            │
│    COMMITTEES  [default: ""]                                                                                         │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

### atr key delete

```
Usage: atr key delete FINGERPRINT

Delete an OpenPGP key.

╭─ Arguments ──────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *  FINGERPRINT  [required]                                                                                           │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

### atr key get

```
Usage: atr key get FINGERPRINT

Get an OpenPGP key.

╭─ Arguments ──────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *  FINGERPRINT  [required]                                                                                           │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

### atr key upload

```
Usage: atr key upload PATH SELECTED_COMMITTEE_NAME

Upload a KEYS file.

╭─ Arguments ──────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *  PATH                     [required]                                                                               │
│ *  SELECTED_COMMITTEE_NAME  [required]                                                                               │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

### atr key user

```
Usage: atr key user [ARGS]

List OpenPGP keys for a user.

╭─ Parameters ─────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ ASF-UID --asf-uid                                                                                                    │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

## atr list

```
Usage: atr list PROJECT VERSION [ARGS]

List all files within a release.

╭─ Arguments ──────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *  PROJECT   [required]                                                                                              │
│ *  VERSION   [required]                                                                                              │
│    REVISION                                                                                                          │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

## atr release

```
Usage: atr release COMMAND

Release operations.

╭─ Commands ───────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ info   Show information about a release.                                                                             │
│ list   List releases for a project.                                                                                  │
│ start  Start a release.                                                                                              │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

### atr release info

```
Usage: atr release info PROJECT VERSION

Show information about a release.

╭─ Arguments ──────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *  PROJECT  [required]                                                                                               │
│ *  VERSION  [required]                                                                                               │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

### atr release list

```
Usage: atr release list PROJECT

List releases for a project.

╭─ Arguments ──────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *  PROJECT  [required]                                                                                               │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

### atr release start

```
Usage: atr release start PROJECT VERSION

Start a release.

╭─ Arguments ──────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *  PROJECT  [required]                                                                                               │
│ *  VERSION  [required]                                                                                               │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

## atr revisions

```
Usage: atr revisions PROJECT VERSION

List all revisions for a release.

╭─ Arguments ──────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *  PROJECT  [required]                                                                                               │
│ *  VERSION  [required]                                                                                               │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

## atr rsync

```
Usage: atr rsync PROJECT VERSION [ARGS]

Rsync a release.

╭─ Arguments ──────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *  PROJECT  [required]                                                                                               │
│ *  VERSION  [required]                                                                                               │
│    SOURCE   [default: .]                                                                                             │
│    TARGET   [default: /]                                                                                             │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

## atr set

```
Usage: atr set PATH [ARGS]

Set a configuration value using dot notation.

╭─ Arguments ──────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *  PATH   [required]                                                                                                 │
│    VALUE                                                                                                             │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Parameters ─────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ STDIN --stdin --no-stdin  [default: False]                                                                           │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

## atr show

```
Usage: atr show PATH

Show a configuration value using dot notation.

╭─ Arguments ──────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *  PATH  [required]                                                                                                  │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

## atr ssh

```
Usage: atr ssh COMMAND

SSH operations.

╭─ Commands ───────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ add     Add an SSH key.                                                                                              │
│ delete  Delete an SSH key.                                                                                           │
│ list    List SSH keys.                                                                                               │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

### atr ssh add

```
Usage: atr ssh add TEXT

Add an SSH key.

╭─ Arguments ──────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *  TEXT  [required]                                                                                                  │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

### atr ssh delete

```
Usage: atr ssh delete FINGERPRINT

Delete an SSH key.

╭─ Arguments ──────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *  FINGERPRINT  [required]                                                                                           │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

### atr ssh list

```
Usage: atr ssh list [ARGS]

List SSH keys.

╭─ Parameters ─────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ ASF-UID --asf-uid                                                                                                    │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

## atr upload

```
Usage: atr upload PROJECT VERSION PATH FILEPATH

Upload a file to a release.

╭─ Arguments ──────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *  PROJECT   [required]                                                                                              │
│ *  VERSION   [required]                                                                                              │
│ *  PATH      [required]                                                                                              │
│ *  FILEPATH  [required]                                                                                              │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

## atr verify

```
Usage: atr verify URL [ARGS]

Verify an artifact.

╭─ Arguments ──────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *  URL  [required]                                                                                                   │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Parameters ─────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ VERBOSE --verbose --no-verbose  [default: False]                                                                     │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

## atr vote

```
Usage: atr vote COMMAND

Vote operations.

╭─ Commands ───────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ resolve   Resolve a vote.                                                                                            │
│ start     Start a vote.                                                                                              │
│ tabulate  Tabulate a vote.                                                                                           │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

### atr vote resolve

```
Usage: atr vote resolve PROJECT VERSION RESOLUTION

Resolve a vote.

╭─ Parameters ─────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *  PROJECT --project        [required]                                                                               │
│ *  VERSION --version        [required]                                                                               │
│ *  RESOLUTION --resolution  [choices: passed, failed] [required]                                                     │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

### atr vote start

```
Usage: atr vote start --mailing-list STR [OPTIONS] PROJECT VERSION [ARGS]

Start a vote.

╭─ Arguments ──────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *  PROJECT  [required]                                                                                               │
│ *  VERSION  [required]                                                                                               │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Parameters ─────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│    REVISION --revision                                                                                               │
│ *  --mailing-list -m                 [required]                                                                      │
│    --duration -d                     [default: 72]                                                                   │
│    --subject -s                                                                                                      │
│    --body -b                                                                                                         │
│    --concerns-noted -c               Comma separated keys of the concern groups that you reviewed, e.g.              │
│                                      atr.tasks.checks.license.headers. Every current concern group must be           │
│                                      acknowledged by its key before a vote can start. The atr check concerns command │
│                                      lists these keys.                                                               │
│    --auto-publish --no-auto-publish  [default: False]                                                                │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

### atr vote tabulate

```
Usage: atr vote tabulate PROJECT VERSION

Tabulate a vote.

╭─ Arguments ──────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *  PROJECT  [required]                                                                                               │
│ *  VERSION  [required]                                                                                               │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
