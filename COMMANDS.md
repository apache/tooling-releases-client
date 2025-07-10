
# atr

```
Usage: atr docs

Show comprehensive CLI documentation in Markdown.
```

## checks

```
Usage: checks COMMAND

Check result operations.

╭─ Commands ───────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ exceptions  Get check exceptions for a release revision.                                                             │
│ failures    Get check failures for a release revision.                                                               │
│ status      Get check status for a release revision.                                                                 │
│ warnings    Get check warnings for a release revision.                                                               │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

### exceptions

```
Usage: exceptions [ARGS] [OPTIONS]

Get check exceptions for a release revision.

╭─ Parameters ─────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *  PROJECT --project           [required]                                                                            │
│ *  VERSION --version           [required]                                                                            │
│ *  REVISION --revision         [required]                                                                            │
│    --members --no-members  -m  [default: False]                                                                      │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

### failures

```
Usage: failures [ARGS] [OPTIONS]

Get check failures for a release revision.

╭─ Parameters ─────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *  PROJECT --project           [required]                                                                            │
│ *  VERSION --version           [required]                                                                            │
│ *  REVISION --revision         [required]                                                                            │
│    --members --no-members  -m  [default: False]                                                                      │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

### status

```
Usage: status [ARGS] [OPTIONS]

Get check status for a release revision.

╭─ Parameters ─────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *  PROJECT --project           [required]                                                                            │
│ *  VERSION --version           [required]                                                                            │
│ *  REVISION --revision         [required]                                                                            │
│    --verbose --no-verbose  -v  [default: False]                                                                      │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

### warnings

```
Usage: warnings [ARGS] [OPTIONS]

Get check warnings for a release revision.

╭─ Parameters ─────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *  PROJECT --project           [required]                                                                            │
│ *  VERSION --version           [required]                                                                            │
│ *  REVISION --revision         [required]                                                                            │
│    --members --no-members  -m  [default: False]                                                                      │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

## config

```
Usage: config COMMAND

Configuration operations.

╭─ Commands ───────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ file  Display the configuration file contents.                                                                       │
│ path  Show the configuration file path.                                                                              │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

### file

```
Usage: file

Display the configuration file contents.
```

### path

```
Usage: path

Show the configuration file path.
```

## dev

```
Usage: dev COMMAND

Developer operations.

╭─ Commands ───────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ stamp  Update version and exclude-newer in pyproject.toml.                                                           │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

### stamp

```
Usage: stamp

Update version and exclude-newer in pyproject.toml.
```

## docs

```
Usage: docs

Show comprehensive CLI documentation in Markdown.
```

## drop

```
Usage: drop [ARGS] [OPTIONS]

Remove a configuration key using dot notation.

╭─ Parameters ─────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *  PATH --path  [required]                                                                                           │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

## jwt

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

### dump

```
Usage: dump

Show decoded JWT payload from stored config.
```

### info

```
Usage: info

Show JWT payload in human-readable form.
```

### refresh

```
Usage: refresh [ARGS] [OPTIONS]

Fetch a JWT using the stored PAT and store it in config.

╭─ Parameters ─────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ ASF-UID --asf-uid                                                                                                    │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

### show

```
Usage: show

Show stored JWT token.
```

## list

```
Usage: list [ARGS] [OPTIONS]

List all files within a release.

╭─ Parameters ─────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *  PROJECT --project    [required]                                                                                   │
│ *  VERSION --version    [required]                                                                                   │
│    REVISION --revision                                                                                               │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

## release

```
Usage: release COMMAND

Release operations.

╭─ Commands ───────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ info   Show information about a release.                                                                             │
│ list   List releases for a project.                                                                                  │
│ start  Start a release.                                                                                              │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

### start

```
Usage: start [ARGS] [OPTIONS]

Start a release.

╭─ Parameters ─────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *  PROJECT --project  [required]                                                                                     │
│ *  VERSION --version  [required]                                                                                     │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

## revisions

```
Usage: revisions [ARGS] [OPTIONS]

List all revisions for a release.

╭─ Parameters ─────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *  PROJECT --project  [required]                                                                                     │
│ *  VERSION --version  [required]                                                                                     │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

## set

```
Usage: set [ARGS] [OPTIONS]

Set a configuration value using dot notation.

╭─ Parameters ─────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *  PATH --path    [required]                                                                                         │
│ *  VALUE --value  [required]                                                                                         │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

## upload

```
Usage: upload [ARGS] [OPTIONS]

Upload a file to a release.

╭─ Parameters ─────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *  PROJECT --project    [required]                                                                                   │
│ *  VERSION --version    [required]                                                                                   │
│ *  PATH --path          [required]                                                                                   │
│ *  FILEPATH --filepath  [required]                                                                                   │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

## version

```
Usage: version

Show the version of the client.
```

## vote

```
Usage: vote COMMAND

Vote operations.

╭─ Commands ───────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ start  Start a vote.                                                                                                 │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
