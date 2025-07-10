
# atr

```
Usage: atr docs

Show comprehensive CLI documentation in Markdown.
```

## atr checks

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
│ *  PROJECT   [required]                                                                                              │
│ *  VERSION   [required]                                                                                              │
│ *  REVISION  [required]                                                                                              │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Parameters ─────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ VERBOSE --verbose --no-verbose  -v  [default: False]                                                                 │
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
│ env    Show the environment variables.                                                                               │
│ stamp  Update version and exclude-newer in pyproject.toml.                                                           │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

### atr dev env

```
Usage: env

Show the environment variables.
```

### atr dev stamp

```
Usage: stamp

Update version and exclude-newer in pyproject.toml.
```

## atr docs

```
Usage: docs

Show comprehensive CLI documentation in Markdown.
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
│ start  Start a vote.                                                                                                 │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
