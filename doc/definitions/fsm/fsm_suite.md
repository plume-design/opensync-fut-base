# FSM testing

## Overview

This test suite tests the Flow Service Manager (FSM). FSM is the foundation of the access control service, and provides
the infrastructure for managing the data traffic flows. In addition, FSM provides the required hooks for implementing
cybersecurity, parental controls, and future services.

What is essential for the FSM operation is the ability of OVS to monitor and manipulate the relevant traffic flows. OVS
blocks, filters, forwards, and prioritizes the messages. All of these OVS activities are programmable from the Cloud
using OVSDB.

Tests can be split into two categories:

- complex "end-to-end" tests that combine functional parts into complete services
- "moving parts" tests which provide verification for the complex tests
