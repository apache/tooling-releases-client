# apache-releases-client

This is a command-line client for the Apache Trusted Releases (ATR) platform, utilising the ATR API to perform actions. The ATR provides Apache Software Foundation (ASF) participants with an easy way to release software. The goal of this client is to make things even easier, especially for those who prefer command-line interface (CLI) or terminal user interface (TUI) workflows.

This project is maintained by ASF Tooling. As of July 2025, we have only just started work on this client, so there isn't anything to test yet. As we add functionality, we'll update this README. We will be focusing on the CLI first of all, keeping the TUI as a long-term goal.

Please feedback to the ASF Tooling mailing list, or the `#apache-trusted-releases` Slack. We welcome contributions already, and you may file issues or create pull requests. To assist us in reviewing your code, please adhere to our style guidelines as noted in the codebase. Thank you.

The ATR API is not stable, so please do not rely on its schema. The client CLI is also not stable, so please do not use it in unattended scripts.

## Quick Start

1. Installation of **atr** client from within a target directory.

   ```
   python3 -m venv venv
   source venv/bin/activate
   pip3 install -U pip setuptools wheel
   pip3 install git+https://github.com/apache/tooling-releases-client atr
   atr --version
   ```

2. Configuration

   ```
   atr set asf.uid <your asf id>
   atr set tokens.pat
   atr jwt refresh
   ```

   The `atr set tokens.pat` command prompts for your PAT from the ATR site, without echoing it. In scripts, pipe the PAT to `atr set tokens.pat --stdin` instead. Do not pass the PAT as a command line argument, because it would then be recorded in your shell history and exposed to other local processes.

If you do not have a compatible version of Python (we currently require 3.12 or higher), then you can try using the following commands:

```
curl -LsSf https://astral.sh/uv/install.sh | sh
uv tool install "apache-trusted-releases @ git+https://github.com/apache/tooling-releases-client"
```

And you should then have an `atr` command available.
