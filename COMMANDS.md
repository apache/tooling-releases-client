
# atr

```
Usage: atr docs

Show comprehensive CLI documentation in Markdown.
```

## atr announce

```
Usage: announce [ARGS] [OPTIONS]

Announce a release.

╭─ Arguments ──────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *  PROJECT   [required]                                                                                              │
│ *  VERSION   [required]                                                                                              │
│ *  REVISION  [required]                                                                                              │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Parameters ─────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *  MAILING-LIST --mailing-list  -m  [required]                                                                       │
│    SUBJECT --subject            -s                                                                                   │
│    BODY --body                  -b                                                                                   │
│    PATH-SUFFIX --path-suffix    -p                                                                                   │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

## atr checks

```
Usage: checks COMMAND

Check result operations.

╭─ Commands ───────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ exceptions  Get check exceptions for a release revision.                                                             │
│ failures    Get check failures for a release revision.                                                               │
│ status      Get check status for a release revision.                                                                 │
│ wait        Wait for checks to be completed.                                                                         │
│ warnings    Get check warnings for a release revision.                                                               │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

### atr checks exceptions

```
Usage: exceptions [ARGS] [OPTIONS]

Get check exceptions for a release revision.

╭─ Arguments ──────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *  PROJECT   [required]                                                                                              │
│ *  VERSION   [required]                                                                                              │
│ *  REVISION  [required]                                                                                              │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Parameters ─────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ MEMBERS --members --no-members  -m  [default: False]                                                                 │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

### atr checks failures

```
Usage: failures [ARGS] [OPTIONS]

Get check failures for a release revision.

╭─ Arguments ──────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *  PROJECT   [required]                                                                                              │
│ *  VERSION   [required]                                                                                              │
│ *  REVISION  [required]                                                                                              │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Parameters ─────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ MEMBERS --members --no-members  -m  [default: False]                                                                 │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

### atr checks status

```
Usage: status [ARGS] [OPTIONS]

Get check status for a release revision.

╭─ Arguments ──────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *  PROJECT  [required]                                                                                               │
│ *  VERSION  [required]                                                                                               │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Parameters ─────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ REVISION --revision                                                                                                  │
│ VERBOSE --verbose --no-verbose  -v  [default: False]                                                                 │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

### atr checks wait

```
Usage: wait [ARGS] [OPTIONS]

Wait for checks to be completed.

╭─ Arguments ──────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *  PROJECT  [required]                                                                                               │
│ *  VERSION  [required]                                                                                               │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Parameters ─────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ REVISION --revision                                                                                                  │
│ TIMEOUT --timeout    -t  [default: 60]                                                                               │
│ INTERVAL --interval  -i  [default: 500]                                                                              │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

### atr checks warnings

```
Usage: warnings [ARGS] [OPTIONS]

Get check warnings for a release revision.

╭─ Arguments ──────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *  PROJECT   [required]                                                                                              │
│ *  VERSION   [required]                                                                                              │
│ *  REVISION  [required]                                                                                              │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Parameters ─────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ MEMBERS --members --no-members  -m  [default: False]                                                                 │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

## atr config

```
Usage: config COMMAND

Configuration operations.

╭─ Commands ───────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ file  Display the configuration file contents.                                                                       │
│ path  Show the configuration file path.                                                                              │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

### atr config file

```
Usage: file

Display the configuration file contents.
```

### atr config path

```
Usage: path

Show the configuration file path.
```

## atr dev

```
Usage: dev COMMAND

Developer operations.

╭─ Commands ───────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ delete  Delete a release.                                                                                            │
│ env     Show the environment variables.                                                                              │
│ pat     Read a PAT from development configuration.                                                                   │
│ stamp   Update version and exclude-newer in pyproject.toml.                                                          │
│ token   Generate a random alphabetical token.                                                                        │
│ user    Show the value of $USER.                                                                                     │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

### atr dev delete

```
Usage: delete [ARGS]

Delete a release.

╭─ Arguments ──────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *  PROJECT  [required]                                                                                               │
│ *  VERSION  [required]                                                                                               │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

### atr dev env

```
Usage: env

Show the environment variables.
```

### atr dev pat

```
Usage: pat

Read a PAT from development configuration.
```

### atr dev stamp

```
Usage: stamp

Update version and exclude-newer in pyproject.toml.
```

### atr dev token

```
Usage: token

Generate a random alphabetical token.
```

### atr dev user

```
Usage: user

Show the value of $USER.
```

## atr docs

```
Usage: docs

Show comprehensive CLI documentation in Markdown.
```

## atr draft

```
Usage: draft COMMAND

Draft operations.

╭─ Commands ───────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ delete  Delete a draft release.                                                                                      │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

## atr drop

```
Usage: drop [ARGS]

Remove a configuration key using dot notation.

╭─ Arguments ──────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *  PATH  [required]                                                                                                  │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

## atr jwt

```
Usage: jwt COMMAND

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
Usage: dump

Show decoded JWT payload from stored config.
```

### atr jwt info

```
Usage: info

Show JWT payload in human-readable form.
```

### atr jwt refresh

```
Usage: refresh [ARGS] [OPTIONS]

Fetch a JWT using the stored PAT and store it in config.

╭─ Parameters ─────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ ASF-UID --asf-uid                                                                                                    │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

### atr jwt show

```
Usage: show

Show stored JWT token.
```

## atr keys

```
Usage: keys

Keys operations.
```

## atr list

```
Usage: list [ARGS]

List all files within a release.

╭─ Arguments ──────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *  PROJECT   [required]                                                                                              │
│ *  VERSION   [required]                                                                                              │
│    REVISION                                                                                                          │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

## atr release

```
Usage: release COMMAND

Release operations.

╭─ Commands ───────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ info   Show information about a release.                                                                             │
│ list   List releases for a project.                                                                                  │
│ start  Start a release.                                                                                              │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

### atr release start

```
Usage: start [ARGS]

Start a release.

╭─ Arguments ──────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *  PROJECT  [required]                                                                                               │
│ *  VERSION  [required]                                                                                               │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

## atr revisions

```
Usage: revisions [ARGS]

List all revisions for a release.

╭─ Arguments ──────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *  PROJECT  [required]                                                                                               │
│ *  VERSION  [required]                                                                                               │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

## atr set

```
Usage: set [ARGS]

Set a configuration value using dot notation.

╭─ Arguments ──────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *  PATH   [required]                                                                                                 │
│ *  VALUE  [required]                                                                                                 │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

## atr ssh

```
Usage: ssh COMMAND

SSH operations.

╭─ Commands ───────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ add     Add an SSH key.                                                                                              │
│ delete  Delete an SSH key.                                                                                           │
│ list    List SSH keys.                                                                                               │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

### atr ssh add

```
Usage: add [ARGS]

Add an SSH key.

╭─ Arguments ──────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *  TEXT  [required]                                                                                                  │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

## atr upload

```
Usage: upload [ARGS]

Upload a file to a release.

╭─ Arguments ──────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *  PROJECT   [required]                                                                                              │
│ *  VERSION   [required]                                                                                              │
│ *  PATH      [required]                                                                                              │
│ *  FILEPATH  [required]                                                                                              │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

## atr vote

```
Usage: vote COMMAND

Vote operations.

╭─ Commands ───────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ resolve  Resolve a vote.                                                                                             │
│ start    Start a vote.                                                                                               │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

### atr vote resolve

```
Usage: resolve [ARGS] [OPTIONS]

Resolve a vote.

╭─ Parameters ─────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *  PROJECT --project        [required]                                                                               │
│ *  VERSION --version        [required]                                                                               │
│ *  RESOLUTION --resolution  [choices: passed, failed] [required]                                                     │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
