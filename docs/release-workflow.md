# Release workflow

**WARNING: The ATR client is in flux, so these instructions may become out of date.**

## Summary

[Get a PAT from the Tokens page](https://release-test.apache.org/tokens) and [install uv](https://docs.astral.sh/uv/getting-started/installation/).

```
git clone https://github.com/apache/tooling-releases-client
cd tooling-releases-client
uv run atr --version
alias atr="uv run atr"
```

Now you have an `atr` command. Set a couple of required configuration values. The second command prompts for your PAT without echoing it.

```
atr set asf.uid "$ASF_UID"
atr set tokens.pat
```

You can now create a release.

```
atr release start your-project 0.1+test
```

Your release is in the ① COMPOSE phase.

```
atr upload your-project 0.1+test example.txt "$FILE_TO_UPLOAD"
atr check wait your-project 0.1+test
atr vote start your-project 0.1+test 00002 -m "${ASF_UID}@apache.org"
```

Your release is in the ② VOTE phase.

```
atr vote resolve your-project 0.1+test passed
```

Your release is in the ③ FINISH phase.

```
atr announce your-project 0.1+test 00003 -m "${ASF_UID}@apache.org"
```

Your release is published and immutable.

## Details

If you run into problems with the commands above, this section may help you. It also gives extra commands that you can try, and more information about how the ATR client works.

### Installation

To test the release workflow, [log in to the `release-test` instance of ATR using ASF OAuth](https://release-test.apache.org/) and then [go to your Tokens page](https://release-test.apache.org/tokens). Where it says "Generate new token" in the "Personal Access Tokens (PATs)" section, write a brief description of your pat (e.g. "ATR client test") and then press "Generate token". Your PAT will appear as a flash message at the top of the page; write this down safely somewhere now, because it will not be visible again. We do not store PATs in the ATR, only PAT hashes.

[Install uv](https://docs.astral.sh/uv/getting-started/installation/), and make sure you have a copy of [the ATR client repository](https://github.com/apache/tooling-releases-client) locally. You can then test the ATR client using the following command:

```
uv run atr --version
```

This will install the ATR client to `.venv/bin/atr` in the `tooling-releases-client` directory. You can also add that `atr` to your `$PATH` in various ways, or just set `alias atr="uv run atr"`. The rest of this guide will assume that you have set this alias.

If you have `pip3` available, you can also run the following to install the `atr` client command:

```
pip3 install git+https://github.com/apache/tooling-releases-client
```

This will place the `atr` command in the directory that `pip3` is configured to add commands to.

### Configuration

Add your ASF UID and PAT to configuration.

```
atr set asf.uid "$ASF_UID"
atr set tokens.pat
```

Your `"$ASF_UID"` is just the short ASF username, e.g. `wave`, `tn`, or `sbp` for the ASF Tooling team. The second command prompts for your PAT without echoing it; paste the value you recorded earlier from the website. If you didn't record it, you can always generate a new one as you can have multiple PATs. In scripts, pipe the PAT to `atr set tokens.pat --stdin` instead of using the prompt. Do not pass the PAT as a command line argument, because it would then be recorded in your shell history and exposed to other local processes.

The configuration path depends on your OS, but you can find it using `atr config path`. On macOS, for example, it will be at:

```
/Users/$USER/Library/Application Support/atr/atr.yaml
```

### Compose

To start a release for the `your-project` project, with release version `0.1+test`, you would do:

```
atr release start your-project 0.1+test
```

Your release is then in the ① COMPOSE phase. You must add a file to be able to start a vote from here. You can use `rsync` or the upload form on the ATR website, but there is also an `atr upload` command for easier testing, and we plan to add an `rsync` wrapper too. To upload a file at `"$FILE_TO_UPLOAD"` to the path `example.txt` in the draft, use the following commands.

```
atr upload your-project 0.1+test example.txt "$FILE_TO_UPLOAD"
atr check wait your-project 0.1+test
```

To see the status of the checks here, you could run `atr check status your-project 0.1+test 00002`. You need to know the revision to get the status, but we plan to make this command use the most recent revision if omitted.

To generate a CycloneDX SBOM for an uploaded artifact, augmented automatically for NTIA conformance, use `atr sbom generate`. The SBOM appears beside the artifact in a new revision. You can then sign it with your OpenPGP key and upload the detached signature.

```
atr sbom generate your-project 0.1+test example-0.1.tar.gz --wait
atr sign your-project 0.1+test example-0.1.tar.gz.cdx.json --key ~/signing-key.asc --upload
```

The sign command downloads the SBOM, signs it locally using rPGP, and writes the detached signature next to the download. With `--upload` it also uploads the signature to the draft, creating a new revision, after checking that the key is registered for the project's committee; by default nothing is uploaded, so when signing many artifacts you can gather the signatures locally and upload them together in a single revision using `atr rsync`. The command selects the newest valid signing subkey automatically, skipping expired or revoked components, and prompts for a passphrase when the key is protected. These client checks are advisory: ATR verifies every uploaded signature against the registered committee certificates, so conditions which the client does not detect, such as a rotated signing subkey which is not yet in the registered certificate, are reported by the server checks after upload. Sign the SBOM only after all steps which modify it, because augmentation and vulnerability scanning rewrite the file. There is also a general `atr download` command to fetch any release file.

To export a key for signing, use the following commands, and delete the exported file when you no longer need it.

```
gpg --export-secret-keys --armor --output ~/signing-key.asc "$KEYID"
chmod 600 ~/signing-key.asc
atr set signing.key ~/signing-key.asc
```

If you keep your primary key offline, `gpg --export-secret-subkeys` works too, provided that your key has a signing subkey. Keys held only in gpg-agent or on a hardware token cannot be exported this way, and are not yet supported for signing.

### Vote

```
atr vote start your-project 0.1+test 00002 -m "${ASF_UID}@apache.org"
```

Your release is in the ② VOTE phase. You must use the revision number here. We will not support automatically finding the latest revision number in this case, because you need to know exactly what the project's participants are voting on.

Instead of your ASF email address, you can also use `user-tests@tooling.apache.org` as the value here and then [consult the mailing list archives](https://lists.apache.org/list.html?user-tests@tooling.apache.org) to check that the thread was created.

### Finish

```
atr vote resolve your-project 0.1+test passed
```

Your release is in the ③ FINISH phase.

```
atr announce your-project 0.1+test 00003 -m "${ASF_UID}@apache.org"
```

Like with the vote you must know your revision to be able to announce your release. And again, instead of your ASF email address, you can also use `user-tests@tooling.apache.org` as the value here and then [consult the mailing list archives](https://lists.apache.org/list.html?user-tests@tooling.apache.org) to check that the thread was created.

### Conclusion

If you are an admin you can delete your test at any time, including after announcement, using `atr dev delete your-project 0.1+test`.

For an actual example of this workflow, consult [`cli_workflow.t`](https://github.com/apache/tooling-releases-client/blob/main/tests/cli_workflow.t) in the ATR client test suite.
