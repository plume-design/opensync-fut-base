# Platform Manager - PM test suite

The `Platform Manager - PM` implements specific platform-related features which can not be covered by other managers:

- Nickname synchronization between device `GUI` and the Cloud.
- Cloud-managed device parental control, also known as `device freeze`.
- Device thermal management by regulating fan rotation speed.
- Device `LED` management
- Log management:
    - collecting and uploading logs and system information upon request from the Cloud - also known as `logpull`.
    - Setting the loging severity for running modules.
