#!/usr/bin/env python3
import os

import aws_cdk as cdk

from streamlitecs.streamlitecs_stack import StreamlitecsStack


app = cdk.App()
StreamlitecsStack(app, "StreamlitecsStack")

app.synth()
