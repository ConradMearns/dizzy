# Getting Dizzy

## Core Principals

- Command Query Responsability Seperation
- Event Sourcing
- Dependency Injection
- Command Queueing
- Entity Component Systems

## Suggested Stack (for now)

- LinkML
- Python
- Incus - https://linuxcontainers.org/incus/docs/main/

## Dreams...

- ESP32 integration

## Event Storming

You should have

- Users
- Commands
- Domain Events
- Domain Entities
- Policies
- Procedures

## Refining and Optimizing

- Telemetry
- Queries
- Mutations

# Reference?

```mermaid
flowchart LR
  RANTS["rants<br>papers<br>scribbles<br>dreams<br>nightmares"]
  USERS["users"]
  COMMANDS["commands"]
  SYSTEMS["systems"]
  EVENTS["events"]
  DOMAIN["domain components"]
  POLICY["policy"]

  RANTS -->|"generate"| DOMAIN
  RANTS -->|"identify"| USERS
  USERS -->|"extract"| COMMANDS
  COMMANDS -->|"map to"| SYSTEMS
  SYSTEMS -->|"emit"| EVENTS
  EVENTS -->|"update"| DOMAIN
  SYSTEMS -->|"define"| DOMAIN
  DOMAIN -->|"inform"| SYSTEMS
  POLICY -->|"issue"| COMMANDS
  COMMANDS -->|"trigger"| POLICY
  EVENTS -->|"activate"| POLICY

  style RANTS stroke:#1e1e1e,stroke-width:2,fill:none
  style USERS stroke:#846358,stroke-width:4,fill:none
  style COMMANDS stroke:#1971c2,stroke-width:2,fill:none
  style SYSTEMS stroke:#e03131,stroke-width:2,fill:none
  style EVENTS stroke:#f08c00,stroke-width:2,fill:none
  style DOMAIN stroke:#40c057,stroke-width:2,fill:none
  style POLICY stroke:#6741d9,stroke-width:2,fill:none
```