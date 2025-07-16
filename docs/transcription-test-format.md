# ATR transcript format

We use a transcript format to test the CLI of the ATR client. This is a guide to that format.

Each `.t` transcript file is a stateful session with a console. Commands are prefixed by `"$ "`, `"! "`, or `"* "`, depending on whether they are expected to succeed, fail, or either.

```
$ echo this should succeed
this should succeed

! grep -i "this should fail" /does/not/exist
<.etc.>

* cat /etc/motd
<.etc.>
```

Compare also an [example of a longer file](https://raw.githubusercontent.com/apache/tooling-releases-client/refs/heads/main/tests/cli_workflow.t).

The command must be followed by the expected output of the command. As you can see even from the short example above, certain helpful syntax is permitted to help fully characterise inputs and outputs.

## Syntax

### `<.etc.>`

Any further output is ignored. For example, if you `cat` a large file but only want to match the first two lines:

```
$ cat large-file.txt
first line
second line
<.etc.>
```

### `<.exit.>`

All tests stop. This is useful for debugging when you don't want to test the rest of the file for some reason, e.g. because you know it's broken. You can also use this to add a long comment to the bottom of a file.

```
$ echo trivial test
trivial test

<.exit.>

$ obviously broken test
???
```

### `<.skip.>`

You can use `<.etc.>` to skip the entire rest of the input, but `<.skip.>` allows you to skip to the next interesting thing within a line, or to consume the rest of the line. It's a non-greedy regular expression match. In practice, it's often useful for searching within lines.

```
$ echo we only want to match the middle of this line
<.skip.>match the middle<.skip.>
```

### `<.stderr.>`

The ATR transcript format captures all of stdout first, then all of stderr. To indicate that you are now capturing stderr, use `<.stderr.>` by itself on a line.

```
$ dc -e "1 0 /" | less
<.stderr.>

Math error: divide by 0
    0: (main)
```

If a command is expected to have both stdout and stderr output, stdout must be characterised first, and stderr separately afterwards. We do not support interleaving.

### `<# comment #>`

To add a comment anywhere, use the `<# comment #>` syntax. We recommend using lower case and no trailing punctuation for comments.

```
<# test that df -h returns 0 #>
$ df -h /
<.etc.>
```

### `<?capture?>`

Sometimes it is necessary to capture part of an output to use later on. We only support capturing a whole line.

```
$ dc -e "2 3 + p"
<?sum?>
```

The output of this `dc` command is now stored in the `sum` variable.


### `<!use!>`

The `<!use!>` syntax allows you to use a stored variable. Stored variables can be used in inputs and outputs.

```
$ dc -e "2 3 + p"
<?five?>

$ test <!five!> -eq 5

$ dc -e "7 2 - p"
<!five!>
```

## Origin

This was inspired by the (different, more fully featured) [transcript test format](https://pkg.go.dev/github.com/rogpeppe/go-internal/testscript) in the Golang standard library, which was [originally developed by Russ Cox](https://x.com/_myitcv/status/1522687481447129088). Cox was, in turn, _presumably_ inspired by [Cram](https://bitheap.org/cram/), which is an independent implementation of the earlier [unified test format developed for Mercurial](https://wiki.mercurial-scm.org/WritingTests?action=recall&rev=28#Writing_a_shell_script_test).

## TODO

Does this format need a name? What would we call it? Perhaps _Transcript Ace_, after [reverse transcriptase](https://en.wikipedia.org/wiki/Reverse_transcriptase)? But it's more of a technique than a format. You can easily port this to another language, and adapt it.
