# Make an Apache release with `atr`

The `atr` client takes a release to publication and announcement without you ever needing the ATR website, apart from a one time token setup. This guide follows one such release, Apache Example 1.0.0, all the way.

## Before you begin

Install the client:

```
uv tool install "apache-trusted-releases @ git+https://github.com/apache/tooling-releases-client"
```

Create a PAT on ATR's [Tokens page](https://releases.apache.org/tokens), then set your ASF UID and enter the PAT at the prompt. The prompt won't echo what you type in.

```
atr set asf.uid $YOUR_ASF_UID
atr set tokens.pat
```

That's all the authentication that you need to do, until your PAT expires.

Ensure that your public signing key is registered with your committee if it isn't already:

```
atr key add public.asc example
```

## Compose

Start the draft:

```
atr release start example 1.0.0
```

Every artifact needs a detached signature and a checksum beside it. Make them the way that you usually do, e.g. using `gpg` and `shasum`:

```
gpg --armor --detach-sign apache-example-1.0.0.tar.gz
shasum -a 512 apache-example-1.0.0.tar.gz > apache-example-1.0.0.tar.gz.sha512
```

Upload all three files:

```
atr upload example 1.0.0 apache-example-1.0.0.tar.gz apache-example-1.0.0.tar.gz
atr upload example 1.0.0 apache-example-1.0.0.tar.gz.asc apache-example-1.0.0.tar.gz.asc
atr upload example 1.0.0 apache-example-1.0.0.tar.gz.sha512 apache-example-1.0.0.tar.gz.sha512
```

Each `atr upload` command takes the release path, then the local path. Archive uploads pause briefly for validation, and the client waits.

After ATR has performed its checks, read the results:

```
atr check wait example 1.0.0
atr check status example 1.0.0
```

Blockers must be fixed, and `atr check blockers` lists them. Upload corrected files and check again. Concerns need judgment rather than repair, and `atr check concerns` lists them with their group keys, which you acknowledge when you start the vote.

If your candidate is a whole directory tree, register an SSH key with `atr ssh add "$(cat ~/.ssh/id_ed25519.pub)"` and upload it with `atr rsync example 1.0.0 ./candidate/`. If you keep an exported private signing key, `atr sign example 1.0.0 $FILE_PATH $DIRECTORY --key key.asc --upload` downloads ATR's copy of a file, signs it, and uploads the signature. Use an empty `$DIRECTORY`, because it refuses to overwrite.

## Vote

Note `--auto-publish` below. The client has no publish command, and ATR will not announce a release that has not been published to the Apache distribution repository. This flag asks ATR to publish for you the moment the vote passes.

```
atr vote start example 1.0.0 -m dev@example.apache.org \
  --concerns-noted atr.tasks.checks.rat.check --auto-publish
```

This specific command requires a committee member to run it, because automatic publishing requires it.

The subject, body, and duration come from your project's templates and policy. Omit the revision only if you made the latest one yourself, otherwise find it with `atr revisions example 1.0.0` and supply it after the version.

The vote then runs in the mailing list thread that ATR just started, and the voting procedure depends on the voting mode that you selected in ATR. When the voting period ends, if you did not select automatic vote resolution on the website:

```
atr vote tabulate example 1.0.0
atr vote resolve example 1.0.0 passed
```

## Finish

Passing the vote creates a preview of the final release and starts the SVN publication if you asked for it, as in our example with `--auto-publish`. If your project's policy ties release files to external platforms, record those distributions with `atr distribution record`.

Announce using the `atr announce` command:

```
atr announce example 1.0.0 -m announce@example.apache.org
```

If ATR says the release is still publishing, or not yet on the download servers, wait a little and run the same command again. When it succeeds, ATR sends the announcement and the release process is finished.

## Afterwards

`atr verify $URL` checks a published artifact's signature. If you get stuck, the ATR website shows the same releases and checks that the client does. `atr docs` prints the full command reference.
